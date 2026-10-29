"""Write unrun DD22 regression sources using accepted fixture plumbing."""
from pathlib import Path
import re
here=Path(__file__).resolve().parent
root=here.parents[4]
p=root/"Source/OneBossFight/Tests/RPGBossHealPunishAdaptersTests.cpp"
t=(root/"Source/OneBossFight/Tests/RPGBossShockwaveAdaptersTests.cpp").read_text(encoding="utf-8").replace("Shockwave","HealPunish")
fields=["bEnabled","MinRange","MaxRange","Cooldown","Damage","FlightTime","MinSpeed","MaxSpeed","JavelinRadius","JavelinMaxRange","SpawnSockets","AimHeight","bRespondToHeal","bCancelJavelinsOnInterrupt"]
floats=["MinRange","MaxRange","Cooldown","Damage","FlightTime","MinSpeed","MaxSpeed","JavelinRadius","JavelinMaxRange","AimHeight"]
begin=t.index("\tFRPGHealPunishConfig RecordA()");end=t.index("\tTArray<const UActorComponent*> Owned",begin)
block=r'''
	FRPGHealPunishConfig RecordA()
	{
		FRPGHealPunishConfig R;
		R.bEnabled=false; R.MinRange=0.f; R.MaxRange=0.5f; R.Cooldown=0.f; R.Damage=0.f;
		R.FlightTime=0.05f; R.MinSpeed=0.25f; R.MaxSpeed=0.25f; R.JavelinRadius=0.125f; R.JavelinMaxRange=0.5f;
		R.SpawnSockets={TEXT("Javelin.Emit"),TEXT("hand-l")}; R.AimHeight=-1.0e6f; R.bRespondToHeal=false; R.bCancelJavelinsOnInterrupt=false;
		return R;
	}
	FRPGHealPunishConfig RecordB()
	{
		FRPGHealPunishConfig R;
		R.bEnabled=true; R.MinRange=17.5f; R.MaxRange=1150.f; R.Cooldown=2.5f; R.Damage=23.5f;
		R.FlightTime=1.5f; R.MinSpeed=110.f; R.MaxSpeed=200.f; R.JavelinRadius=15.5f; R.JavelinMaxRange=4444.f;
		R.SpawnSockets={TEXT("CustomEmit"),TEXT("hand_r")}; R.AimHeight=-25.f; R.bRespondToHeal=true; R.bCancelJavelinsOnInterrupt=true;
		return R;
	}
	FRPGParticipantConfig Config(const FRPGHealPunishConfig& R) { FRPGParticipantConfig C; C.HealPunish=R; return C; }
	FRPGHealPunishConfig Read(const URPGBossHealPunish& C)
	{
		FRPGHealPunishConfig R;
'''
block+="\n".join(f"\t\tR.{n}=C.{n};" for n in fields)
block+="\n\t\treturn R;\n\t}\n\tbool Same(const FRPGHealPunishConfig& A,const FRPGHealPunishConfig& B)\n\t{\n\t\treturn "+" && ".join("A."+n+"==B."+n for n in fields)+";\n\t}\n"
block+=r'''
	struct FRuntime
	{
		bool Pending,Registered,Begun,TickRegistered,CanTick;
		float Cooldown;
		TArray<int32> Counters;
		explicit FRuntime(const URPGBossHealPunish& C)
			: Pending(C.IsPending()),Registered(C.IsRegistered()),Begun(C.HasBegunPlay()),
			  TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()),CanTick(C.PrimaryComponentTick.bCanEverTick),Cooldown(C.GetCooldownRemaining()),
			  Counters{C.GetHealEventCount(),C.GetAcceptedCount(),C.GetReleasedCount(),C.GetDiscardedBusyCount(),C.GetDiscardedRangeCount(),
				C.GetDiscardedSightCount(),C.GetDiscardedCooldownCount(),C.GetDiscardedPendingCount(),C.GetCancelledCount(),C.GetJavelinHitCount(),C.GetJavelinDodgedCount(),C.GetJavelinWorldCount()} {}
		bool SameAs(const FRuntime& O) const
		{
			return Pending==O.Pending&&Registered==O.Registered&&Begun==O.Begun&&TickRegistered==O.TickRegistered
				&&CanTick==O.CanTick&&Cooldown==O.Cooldown&&Counters==O.Counters;
		}
	};
'''
t=t[:begin]+block+t[end:]
begin=t.index("\tTArray<FString> Paths()");end=t.index("\n\tstruct FBad",begin)
t=t[:begin]+"\tTArray<FString> Paths()\n\t{\n\t\treturn {"+",".join('TEXT("HealPunish.'+n+'")' for n in fields)+"};\n\t}\n"+t[end:]
begin=t.index("\tTArray<FBad> BadCases()");end=t.index("\n\tbool HasError",begin)
bad="\tTArray<FBad> BadCases()\n\t{\n\t\tTArray<FBad> Cases;\n"
for n in floats:
    for label,value in [("NaN","std::numeric_limits<float>::quiet_NaN()"),("+Inf","std::numeric_limits<float>::infinity()"),("-Inf","-std::numeric_limits<float>::infinity()")]:
        bad+=f'\t\tCases.Add({{TEXT("{n} {label}"),[](FRPGHealPunishConfig& R){{R.{n}={value};}},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::Field{n}}});\n'
rows=[
("negative min","R.MinRange=-1.f","Negative","MinRange"),("zero max","R.MaxRange=0.f","NotPositive","MaxRange"),
("negative max","R.MaxRange=-1.f","NotPositive","MaxRange"),("equal range","R.MinRange=1.f;R.MaxRange=1.f","MaxNotAboveMin","MaxRange"),
("inverted range","R.MinRange=2.f;R.MaxRange=1.f","MaxNotAboveMin","MaxRange"),("negative cooldown","R.Cooldown=-1.f","Negative","Cooldown"),
("negative damage","R.Damage=-1.f","Negative","Damage"),
("below flight floor","R.FlightTime=std::nextafter(RPGBossHealPunishAdapters::MinAuthoredFlightTime,0.f)","BelowFlightTimeFloor","FlightTime"),
("zero flight","R.FlightTime=0.f","BelowFlightTimeFloor","FlightTime"),("negative flight","R.FlightTime=-1.f","BelowFlightTimeFloor","FlightTime")]
for n in ["MinSpeed","MaxSpeed","JavelinRadius","JavelinMaxRange"]:
    rows.extend([(n+" zero",f"R.{n}=0.f","NotPositive",n),(n+" negative",f"R.{n}=-0.5f","NotPositive",n)])
rows.append(("speed interval inverted","R.MinSpeed=2.f;R.MaxSpeed=1.f","MinSpeedAboveMax","MinSpeed"))
for n in [x for x in floats if x!="Damage"]:
    rows.append((n+" next float above ceiling",f"R.{n}=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity())","AboveCeiling",n))
rows.append(("aim below signed floor","R.AimHeight=std::nextafter(-RPGBossHealPunishAdapters::MaxAuthoredMagnitude,-std::numeric_limits<float>::infinity())","BelowFloor","AimHeight"))
for name,body,token,n in rows:
    bad+=f'\t\tCases.Add({{TEXT("{name}"),[](FRPGHealPunishConfig& R){{{body};}},TEXT("InvalidPunish.{token}"),RPGBossHealPunishAdapters::Field{n}}});\n'
for name,body,token in [
("empty sockets","R.SpawnSockets.Reset()","Missing"),
("late None socket","R.SpawnSockets[1]=NAME_None","Malformed"),
("space socket",'R.SpawnSockets[0]=TEXT("hand left")',"Malformed"),
("tab socket",r'R.SpawnSockets[1]=TEXT("hand\tleft")',"Malformed"),
("control socket",'R.SpawnSockets[1]=FName(*FString::Printf(TEXT("hand%cL"),static_cast<TCHAR>(0x7f)))',"Malformed")]:
    bad+=f'\t\tCases.Add({{TEXT("{name}"),[](FRPGHealPunishConfig& R){{{body};}},TEXT("InvalidDependency.{token}"),RPGBossHealPunishAdapters::FieldSpawnSockets}});\n'
bad+="\t\treturn Cases;\n\t}\n"
t=t[:begin]+bad+t[end:]
begin=t.index("\tTArray<FRPGHealPunishConfig> Valid");end=t.index("\n\treturn true;\n}",begin)
valid=r'''
	TArray<FRPGHealPunishConfig> Valid{RecordA(),RecordB(),FRPGHealPunishConfig()};
	const float Ceiling=RPGBossHealPunishAdapters::MaxAuthoredMagnitude;
	auto Pair=RecordB();Pair.MinRange=std::nextafter(Ceiling,0.f);Pair.MaxRange=Ceiling;Valid.Add(Pair);
	auto EqualSpeed=RecordA();EqualSpeed.MinSpeed=Ceiling;EqualSpeed.MaxSpeed=Ceiling;Valid.Add(EqualSpeed);
'''
for n in ["MaxRange","Cooldown","FlightTime","MaxSpeed","JavelinRadius","JavelinMaxRange","AimHeight"]:
    valid+=f'\t{{auto R=RecordA();R.{n}=Ceiling;Valid.Add(R);}}\n'
valid+=r'''
	auto Damage=RecordA();Damage.Damage=std::numeric_limits<float>::max();Valid.Add(Damage);
	auto Duplicates=RecordA();Duplicates.SpawnSockets={TEXT("hand.l"),TEXT("hand.l")};Valid.Add(Duplicates); // no invented uniqueness/ASCII-only rule
	for(int32 I=0;I<3;++I)
	{
		auto R=RecordB(); if(I==0){R.bEnabled=false;}else if(I==1){R.bRespondToHeal=false;}else{R.bCancelJavelinsOnInterrupt=false;} Valid.Add(R);
	}
	for(const auto& R : Valid)
	{
		FString E=TEXT("stale");
		TestTrue(TEXT("valid zero/floor/fractional/ceiling/signed-aim/equal-speed/duplicate-socket record validates and assigns"),
			RPGBossHealPunishAdapters::ValidateHealPunish(R,E)&&E.IsEmpty()
			&&RPGBossHealPunishAdapters::ConfigureHealPunish(*Sweep,Config(R),E)&&Same(Read(*Sweep),R)&&Runtime.SameAs(FRuntime(*Sweep)));
	}
	auto CheckFirst=[this](const FRPGHealPunishConfig& R,const TCHAR* Token,const TCHAR* Field)
	{
		FString E;RPGBossHealPunishAdapters::ValidateHealPunish(R,E);
		TestTrue(TEXT("validation order"),E.StartsWith(Token)&&E.Contains(Field));
	};
	auto R=RecordB();R.MinRange=-1.f;R.AimHeight=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight);
	R=RecordB();R.MaxRange=std::numeric_limits<float>::infinity();R.Damage=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxRange);
	R=RecordB();R.MinRange=Ceiling;R.MaxRange=Ceiling;
	CheckFirst(R,TEXT("InvalidPunish.MaxNotAboveMin"),RPGBossHealPunishAdapters::FieldMaxRange);
	R=RecordB();R.MinSpeed=1.f;R.MaxSpeed=0.f;
	CheckFirst(R,TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMaxSpeed);
	R=RecordB();R.SpawnSockets.Reset();R.AimHeight=Ceiling*2.f;
	CheckFirst(R,TEXT("InvalidDependency.Missing"),RPGBossHealPunishAdapters::FieldSpawnSockets);
	R=RecordB();R.SpawnSockets.Reset();R.AimHeight=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight);
'''
t=t[:begin]+valid+t[end:]
t=t.replace("Invalid.MoveId = NAME_None","Invalid.SpawnSockets.Reset()").replace("Bad.MoveId = NAME_None","Bad.SpawnSockets.Reset()")
t=t.replace('Input.HealPunish = RecordB();','Input.HealPunish.SpawnSockets[0]=TEXT("ChangedAfterAssign"); Input.HealPunish.SpawnSockets.Add(TEXT("Extra"));\n\tTestTrue(TEXT("native socket array owns an independent copy"),Same(Read(*A),RecordA()));\n\tInput.HealPunish = RecordB();',1)
t=t.replace('TestTrue(TEXT("next compile copies independent record"), Compile(*D, Out).IsReady() && Out.IsValid() && Same(Out->HealPunish, RecordB()));',
'''TestTrue(TEXT("next compile copies independent record"),Compile(*D,Out).IsReady()&&Out.IsValid()&&Same(Out->HealPunish,RecordB()));
	D->HealPunish.SpawnSockets[0]=TEXT("ChangedAfterCompile");
	TestTrue(TEXT("compiled socket array owns an independent copy"),Out.IsValid()&&Same(Out->HealPunish,RecordB()));''')
begin=t.index("bool FRPGHealPunishAuthoringTest::RunTest")
t=t[:begin]+r'''
bool FRPGHealPunishAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	const UScriptStruct* Struct=FRPGHealPunishConfig::StaticStruct();
	int32 Count=0;for(TFieldIterator<FProperty> It(Struct);It;++It){++Count;TestTrue(TEXT("authored field editable"),It->HasAnyPropertyFlags(CPF_Edit));}
	TestEqual(TEXT("exact14 authored properties"),Count,14);
	for(const TCHAR* N : {TEXT("bEnabled"),TEXT("bRespondToHeal"),TEXT("bCancelJavelinsOnInterrupt")})
	{
		TestNotNull(N,CastField<FBoolProperty>(Struct->FindPropertyByName(N)));
		TestNotNull(FString(N)+TEXT(" native bool"),CastField<FBoolProperty>(URPGBossHealPunish::StaticClass()->FindPropertyByName(N)));
	}
	for(const TCHAR* N : {FLOATNAMES})
	{
		TestNotNull(N,CastField<FFloatProperty>(Struct->FindPropertyByName(N)));
		TestNotNull(FString(N)+TEXT(" native float"),CastField<FFloatProperty>(URPGBossHealPunish::StaticClass()->FindPropertyByName(N)));
	}
	const FArrayProperty* Array=CastField<FArrayProperty>(Struct->FindPropertyByName(TEXT("SpawnSockets")));
	const FArrayProperty* NativeArray=CastField<FArrayProperty>(URPGBossHealPunish::StaticClass()->FindPropertyByName(TEXT("SpawnSockets")));
	TestTrue(TEXT("array of names, both record and native"),Array&&NativeArray&&CastField<FNameProperty>(Array->Inner)&&CastField<FNameProperty>(NativeArray->Inner));
	const FStructProperty* Property=CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("HealPunish")));
	TestTrue(TEXT("exact editable Data Asset struct"),Property&&Property->Struct==Struct&&Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGHealPunishConfig Default;
	TestTrue(TEXT("all14 defaults equal native declarations"),Same(Default,Read(*GetDefault<URPGBossHealPunish>())));
	TestTrue(TEXT("explicit default baseline"),Default.bEnabled&&Default.MinRange==400.f&&Default.MaxRange==1000.f&&Default.Cooldown==4.f&&Default.Damage==12.f
		&&Default.FlightTime==1.2f&&Default.MinSpeed==450.f&&Default.MaxSpeed==2500.f&&Default.JavelinRadius==25.f&&Default.JavelinMaxRange==3000.f
		&&Default.SpawnSockets==TArray<FName>{TEXT("JavelinSpawn"),TEXT("hand_l")}&&Default.AimHeight==100.f&&Default.bRespondToHeal&&Default.bCancelJavelinsOnInterrupt);
	auto D=Definition(Default);TestTrue(TEXT("additive default record"),Same(D->HealPunish,Default));
	for(const TCHAR* N : {TEXT("MoveId"),TEXT("DrinkMontage"),TEXT("Flying"),TEXT("bPending"),TEXT("CooldownEnd"),TEXT("PendingSince"),TEXT("SeenGeneration"),TEXT("Released")})
	{TestNull(FString(N)+TEXT(" not an authored field"),Struct->FindPropertyByName(N));}
	AddInfo(TEXT("Reflection/default declarations only. Native A5/drink montage and socket/bone resolution UNRESOLVED; no serialized authoring proof."));
	return true;
}
#endif
'''.replace("FLOATNAMES",",".join('TEXT("'+n+'")' for n in floats))
t=t.replace("LaunchForTest","NotifyHealStartedForTest").replace("Cancel is invoked","CancelAll is invoked")
t=re.sub(r"\beight\b", "fourteen", t).replace("MoveId copied as syntactic identity only; no tracker lookup or sweep execution.",
    "Socket names copied by value; native A5/drink montage/socket resolution is unresolved.")
t=t.replace("wave traversal","projectile traversal")
p.write_text(t,encoding="utf-8")
print("DD22 six regression sources written; UNRUN.")
