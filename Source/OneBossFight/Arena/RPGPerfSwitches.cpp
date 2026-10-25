// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGPerfSwitches.h"
#include "HAL/IConsoleManager.h"

#if !UE_BUILD_SHIPPING
#define RPG_PERF_SWITCH(Func, Name, Help) \
	static TAutoConsoleVariable<int32> CVar##Func(TEXT("rpg.Perf." Name), 1, TEXT(Help), ECVF_Default); \
	bool RPGPerf::Func() { return CVar##Func.GetValueOnGameThread() != 0; }
#else
#define RPG_PERF_SWITCH(Func, Name, Help) \
	bool RPGPerf::Func() { return true; }
#endif

RPG_PERF_SWITCH(FireLights, "FireLights", "0 turns off the point lights of the fire sources (performance experiment).")
#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarFireShadows(TEXT("rpg.Perf.FireShadows"), -1, TEXT("-1 shadows as authored; 0 no fire light casts a shadow; N only the first N braziers keep their shadow (performance experiment)."), ECVF_Default);
int32 RPGPerf::FireShadows() { return CVarFireShadows.GetValueOnGameThread(); }
#else
int32 RPGPerf::FireShadows() { return -1; }
#endif
RPG_PERF_SWITCH(FireFx, "FireFx", "0 hides the fire, smoke and spark particle systems of the fire sources (performance experiment).")
RPG_PERF_SWITCH(GateMist, "GateMist", "0 hides the fog gate cards (performance experiment).")
RPG_PERF_SWITCH(DressingAll, "DressingAll", "0 hides every instanced mesh of the arena dressing (performance experiment).")
RPG_PERF_SWITCH(DressingMist, "DressingMist", "0 hides the translucent mist sheets of the arena dressing (performance experiment).")
RPG_PERF_SWITCH(DressingShadows, "DressingShadows", "0 turns off shadow casting of the arena dressing meshes (performance experiment).")
RPG_PERF_SWITCH(Embers, "Embers", "0 hides the ember field (performance experiment).")
