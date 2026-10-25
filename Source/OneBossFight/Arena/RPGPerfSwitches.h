// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/**
 * Performance experiment switches (console variables rpg.Perf.*, Development builds only; in Shipping every switch is on and nothing is read).
 * They exist to find where the GPU time of the arena goes (2026-10-24: 29 fps on an RTX 3060 against 84 fps in the greybox): the benchmark applies them with -RPGBenchmarkCvars="rpg.Perf.FireLights=0;..." and the arena actors poll them.
 * 1 = on (normal), 0 = off.
 */
namespace RPGPerf
{
	bool FireLights();     // rpg.Perf.FireLights: the point light of every fire source
	/** rpg.Perf.FireShadows: -1 (default) = the shadows as authored; 0 = no fire light casts a shadow; N = only the first N braziers (BrazierFire_00 to BrazierFire_NN, by number) keep their authored shadow, the other lights none. */
	int32 FireShadows();
	bool FireFx();         // rpg.Perf.FireFx: the Cascade fire, smoke and spark systems
	bool GateMist();       // rpg.Perf.GateMist: the cards of the fog gate
	bool DressingAll();    // rpg.Perf.DressingAll: every instanced mesh of the arena dressing
	bool DressingMist();   // rpg.Perf.DressingMist: the translucent mist sheets of the dressing
	bool DressingShadows();// rpg.Perf.DressingShadows: shadow casting of the dressing meshes
	bool Embers();         // rpg.Perf.Embers: the ember field instances
}
