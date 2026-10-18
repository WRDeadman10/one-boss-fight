// Copyright One Boss Fight. All Rights Reserved.

#include "Benchmark/RPGBenchmarkRunner.h"
#include "OneBossFight.h"
#include "Camera/CameraActor.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GenericPlatform/GenericPlatformDriver.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformMemory.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "RHIGlobals.h"
#include "RenderTimer.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "CoreGlobals.h"
#include "Misc/CoreMiscDefines.h"
#include "Misc/DateTime.h"
#include "Misc/EngineVersion.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "UnrealClient.h"

ARPGBenchmarkRunner::ARPGBenchmarkRunner()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
}

void ARPGBenchmarkRunner::BeginPlay()
{
	Super::BeginPlay();

	if (bAutoStart || FParse::Param(FCommandLine::Get(), TEXT("RPGBenchmark")))
	{
		StartBenchmark();
	}
}

void ARPGBenchmarkRunner::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// Never leave the engine uncapped if the level is torn down mid-run.
	if (bRunning)
	{
		AbortBenchmark();
	}
	Super::EndPlay(EndPlayReason);
}

void ARPGBenchmarkRunner::StartBenchmark()
{
	if (bRunning || !GetWorld())
	{
		return;
	}

	ResolvedLabel = RunLabel;
	FString LabelOverride;
	if (FParse::Value(FCommandLine::Get(), TEXT("RPGBenchmarkLabel="), LabelOverride) && !LabelOverride.IsEmpty())
	{
		ResolvedLabel = LabelOverride;
	}

	const int32 ExpectedFrames = FMath::CeilToInt(DurationSeconds * 600.f);
	FrameTimesMs.Reset(ExpectedFrames);
	GameThreadMs.Reset(ExpectedFrames);
	RenderThreadMs.Reset(ExpectedFrames);
	GpuMs.Reset(ExpectedFrames);

	ApplyUncappedFrameRate();

	if (APlayerController* PlayerController = GetWorld()->GetFirstPlayerController())
	{
		FActorSpawnParameters SpawnParams;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		BenchmarkCamera = GetWorld()->SpawnActor<ACameraActor>(GetActorLocation(), FRotator::ZeroRotator, SpawnParams);
		if (BenchmarkCamera)
		{
			PlayerController->SetViewTarget(BenchmarkCamera);
		}
	}

	StartTime = FPlatformTime::Seconds();
	LastTickTime = 0.0;
	bRunning = true;
	SetActorTickEnabled(true);
	UpdateCamera(0.0);

	UE_LOG(LogOneBossFight, Log, TEXT("Benchmark '%s' started: warmup %.1fs, record %.1fs."), *ResolvedLabel, WarmupSeconds, DurationSeconds);
}

void ARPGBenchmarkRunner::AbortBenchmark()
{
	if (!bRunning)
	{
		return;
	}

	bRunning = false;
	SetActorTickEnabled(false);
	RestoreFrameRate();
	UE_LOG(LogOneBossFight, Warning, TEXT("Benchmark '%s' aborted; no results written."), *ResolvedLabel);
}

void ARPGBenchmarkRunner::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!bRunning)
	{
		return;
	}

	// Raw wall-clock frame time; the engine's DeltaSeconds can be clamped and would hide hitches.
	const double Now = FPlatformTime::Seconds();
	const double Elapsed = Now - StartTime;

	if (LastTickTime > 0.0 && Elapsed >= WarmupSeconds)
	{
		FrameTimesMs.Add((Now - LastTickTime) * 1000.0);
		GameThreadMs.Add(FPlatformTime::ToMilliseconds(GGameThreadTime));
		RenderThreadMs.Add(FPlatformTime::ToMilliseconds(GRenderThreadTime));
		GpuMs.Add(FPlatformTime::ToMilliseconds(GGPUFrameTime));
	}
	LastTickTime = Now;

	UpdateCamera(Elapsed);

	if (Elapsed >= WarmupSeconds + DurationSeconds)
	{
		FinishBenchmark();
	}
}

void ARPGBenchmarkRunner::UpdateCamera(double ElapsedSeconds)
{
	if (!BenchmarkCamera)
	{
		return;
	}

	const FVector Center = GetActorLocation();
	const double Angle = 2.0 * PI * ElapsedSeconds / FMath::Max(OrbitPeriodSeconds, 1.f);
	const FVector Location = Center + FVector(FMath::Cos(Angle) * OrbitRadius, FMath::Sin(Angle) * OrbitRadius, OrbitHeight);
	const FRotator Rotation = (Center - Location).Rotation();
	BenchmarkCamera->SetActorLocationAndRotation(Location, Rotation);
}

void ARPGBenchmarkRunner::FinishBenchmark()
{
	bRunning = false;
	SetActorTickEnabled(false);
	RestoreFrameRate();

	LastStats = FRPGFrameStats::Compute(FrameTimesMs, FRPGFrameStats::BudgetForFPS(TargetFPS));
	UE_LOG(LogOneBossFight, Log, TEXT("Benchmark '%s' finished: %s"), *ResolvedLabel, *LastStats.ToLogString());
	UE_LOG(LogOneBossFight, Log, TEXT("Benchmark '%s' %s the %.0f FPS gate (avg FPS and p99)."),
		*ResolvedLabel, LastStats.MeetsTarget(TargetFPS) ? TEXT("PASSED") : TEXT("FAILED"), TargetFPS);

	WriteResults(LastStats);

	if (FParse::Param(FCommandLine::Get(), TEXT("RPGBenchmarkQuit")))
	{
		RequestEngineExit(TEXT("Benchmark finished"));
	}
}

void ARPGBenchmarkRunner::WriteResults(const FRPGFrameStats& Stats) const
{
	const FString Stamp = FDateTime::Now().ToString(TEXT("%Y%m%d_%H%M%S"));
	const FString Folder = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Benchmark"), FString::Printf(TEXT("%s_%s"), *ResolvedLabel, *Stamp));
	IFileManager::Get().MakeDirectory(*Folder, /*Tree=*/true);

	// Per-frame times.
	FString Csv;
	Csv.Reserve(FrameTimesMs.Num() * 8 + 16);
	Csv += TEXT("frame,ms,game_ms,render_ms,gpu_ms\n");
	for (int32 Index = 0; Index < FrameTimesMs.Num(); ++Index)
	{
		Csv += FString::Printf(TEXT("%d,%.4f,%.4f,%.4f,%.4f\n"), Index, FrameTimesMs[Index],
			GameThreadMs[Index], RenderThreadMs[Index], GpuMs[Index]);
	}
	FFileHelper::SaveStringToFile(Csv, *FPaths::Combine(Folder, TEXT("frames.csv")));

	// Summary with the hardware/settings context the performance log requires.
	const FString GpuBrand = FPlatformMisc::GetPrimaryGPUBrand();
	const FGPUDriverInfo DriverInfo = FPlatformMisc::GetGPUDriverInfo(GpuBrand);
	FString OsLabel, OsSubLabel;
	FPlatformMisc::GetOSVersions(OsLabel, OsSubLabel);
	const FPlatformMemoryConstants& MemoryConstants = FPlatformMemory::GetConstants();
	const FPlatformMemoryStats MemoryStats = FPlatformMemory::GetStats();

	FIntPoint Resolution(GSystemResolution.ResX, GSystemResolution.ResY);
	if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport)
	{
		Resolution = GEngine->GameViewport->Viewport->GetSizeXY();
	}

	const TSharedRef<FJsonObject> Json = MakeShared<FJsonObject>();
	Json->SetStringField(TEXT("label"), ResolvedLabel);
	Json->SetStringField(TEXT("timestamp"), Stamp);
	Json->SetStringField(TEXT("map"), GetWorld() ? GetWorld()->GetMapName() : FString());
	Json->SetStringField(TEXT("engine_version"), FEngineVersion::Current().ToString());
	Json->SetStringField(TEXT("build_configuration"), LexToString(FApp::GetBuildConfiguration()));
	Json->SetStringField(TEXT("gpu"), GpuBrand);
	Json->SetStringField(TEXT("gpu_driver_user"), DriverInfo.UserDriverVersion);
	Json->SetStringField(TEXT("gpu_driver_internal"), DriverInfo.InternalDriverVersion);
	Json->SetStringField(TEXT("cpu"), FPlatformMisc::GetCPUBrand());
	Json->SetNumberField(TEXT("ram_gb"), MemoryConstants.TotalPhysicalGB);
	Json->SetStringField(TEXT("os"), OsLabel + TEXT(" ") + OsSubLabel);
	Json->SetNumberField(TEXT("resolution_x"), Resolution.X);
	Json->SetNumberField(TEXT("resolution_y"), Resolution.Y);
	Json->SetNumberField(TEXT("warmup_seconds"), WarmupSeconds);
	Json->SetNumberField(TEXT("duration_seconds"), DurationSeconds);
	Json->SetNumberField(TEXT("frames"), Stats.FrameCount);
	Json->SetNumberField(TEXT("avg_fps"), Stats.AverageFPS);
	Json->SetNumberField(TEXT("avg_ms"), Stats.AverageMs);
	Json->SetNumberField(TEXT("median_ms"), Stats.MedianMs);
	Json->SetNumberField(TEXT("p95_ms"), Stats.P95Ms);
	Json->SetNumberField(TEXT("p99_ms"), Stats.P99Ms);
	Json->SetNumberField(TEXT("min_ms"), Stats.MinMs);
	Json->SetNumberField(TEXT("max_ms"), Stats.MaxMs);
	Json->SetNumberField(TEXT("budget_ms"), Stats.BudgetMs);
	Json->SetNumberField(TEXT("frames_over_budget"), Stats.FramesOverBudget);

	// Thread timings overlap in the render pipeline; compare each against the budget, do not add them.
	const FRPGFrameStats GameStats = FRPGFrameStats::Compute(GameThreadMs, Stats.BudgetMs);
	const FRPGFrameStats RenderStats = FRPGFrameStats::Compute(RenderThreadMs, Stats.BudgetMs);
	const FRPGFrameStats GpuStats = FRPGFrameStats::Compute(GpuMs, Stats.BudgetMs);
	Json->SetNumberField(TEXT("game_thread_avg_ms"), GameStats.AverageMs);
	Json->SetNumberField(TEXT("game_thread_p99_ms"), GameStats.P99Ms);
	Json->SetNumberField(TEXT("render_thread_avg_ms"), RenderStats.AverageMs);
	Json->SetNumberField(TEXT("render_thread_p99_ms"), RenderStats.P99Ms);
	Json->SetNumberField(TEXT("gpu_avg_ms"), GpuStats.AverageMs);
	Json->SetNumberField(TEXT("gpu_p99_ms"), GpuStats.P99Ms);
	Json->SetNumberField(TEXT("target_fps"), TargetFPS);
	Json->SetBoolField(TEXT("meets_target"), Stats.MeetsTarget(TargetFPS));
	Json->SetNumberField(TEXT("used_physical_mb"), static_cast<double>(MemoryStats.UsedPhysical) / (1024.0 * 1024.0));
	Json->SetNumberField(TEXT("peak_used_physical_mb"), static_cast<double>(MemoryStats.PeakUsedPhysical) / (1024.0 * 1024.0));

	FString JsonText;
	const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonText);
	FJsonSerializer::Serialize(Json, Writer);
	FFileHelper::SaveStringToFile(JsonText, *FPaths::Combine(Folder, TEXT("summary.json")));

	UE_LOG(LogOneBossFight, Log, TEXT("Benchmark results written to %s"), *Folder);
}

void ARPGBenchmarkRunner::ApplyUncappedFrameRate()
{
	if (bFrameRateOverridden)
	{
		return;
	}

	IConsoleVariable* MaxFPS = IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS"));
	IConsoleVariable* VSync = IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync"));
	if (MaxFPS)
	{
		SavedMaxFPS = MaxFPS->GetFloat();
		MaxFPS->Set(0.f, ECVF_SetByConsole);
	}
	if (VSync)
	{
		SavedVSync = VSync->GetInt();
		VSync->Set(0, ECVF_SetByConsole);
	}
	if (GEngine)
	{
		bSavedSmoothFrameRate = GEngine->bSmoothFrameRate;
		bSavedFixedFrameRate = GEngine->bUseFixedFrameRate;
		GEngine->bSmoothFrameRate = false;
		GEngine->bUseFixedFrameRate = false;
	}
	bFrameRateOverridden = true;
}

void ARPGBenchmarkRunner::RestoreFrameRate()
{
	if (!bFrameRateOverridden)
	{
		return;
	}

	if (IConsoleVariable* MaxFPS = IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS")))
	{
		MaxFPS->Set(SavedMaxFPS, ECVF_SetByConsole);
	}
	if (IConsoleVariable* VSync = IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync")))
	{
		VSync->Set(SavedVSync, ECVF_SetByConsole);
	}
	if (GEngine)
	{
		GEngine->bSmoothFrameRate = bSavedSmoothFrameRate;
		GEngine->bUseFixedFrameRate = bSavedFixedFrameRate;
	}
	bFrameRateOverridden = false;
}
