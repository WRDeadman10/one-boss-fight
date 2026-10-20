<#
.SYNOPSIS
  Runs the packaged fight benchmark once per variant and prints one comparison line each.

.DESCRIPTION
  Each variant is a label and the console variables applied at launch (-ExecCmds). Change one thing per variant
  against the same base so the effect of each is clear. Summaries are copied to Documentation\PerfCaptures.
  Close other heavy apps first.

.EXAMPLE
  .\Scripts\RunVariants.ps1
#>
param(
	[string]$Map = '/Game/OneBossFight/Levels/L_Greybox'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Base = 'r.DynamicGlobalIlluminationMethod 0,r.ReflectionMethod 2'

# Second round: the first round showed TSR costs about 3.5 ms of GPU; everything below keeps GI and reflections as in
# round one and changes one thing against the FXAA row.
$Fx = "$Base,r.AntiAliasingMethod 1"
$Variants = @(
	@('w_taa', "$Base,r.AntiAliasingMethod 2"),
	@('w_fxaa', $Fx),
	@('w_fxaa_noshadow', "$Fx,r.ShadowQuality 0"),
	@('w_fxaa_noparticles', "$Fx,r.ParticleLODBias 10"),
	@('w_fxaa_vsm_off', "$Fx,r.Shadow.Virtual.Enable 0"),
	@('w_fxaa_nofog', "$Fx,r.Fog 0"),
	@('w_taa_b', "$Base,r.AntiAliasingMethod 2")
)

foreach ($Variant in $Variants) {
	$Label = $Variant[0]
	$Extra = '-RPGBenchmarkFight -ExecCmds="' + $Variant[1] + '"'
	& (Join-Path $PSScriptRoot 'RunBenchmark.ps1') -Label $Label -Map $Map -ExtraArgs $Extra | Out-Null
	$Dir = Get-ChildItem (Join-Path $ProjectRoot 'Saved\StagedBuilds\Windows\OneBossFight\Saved\Benchmark') -Directory -Filter "${Label}_*" |
		Sort-Object LastWriteTime -Descending | Select-Object -First 1
	$S = Get-Content (Join-Path $Dir.FullName 'summary.json') -Raw | ConvertFrom-Json
	'{0,-24} avg={1,6:N1} fps  p95={2,5:N2}  p99={3,6:N2}  max={4,6:N1}  game={5:N1}/{6:N1}  render={7:N1}/{8:N1}  gpu={9:N1}/{10:N1}  meets={11}' -f `
		$Label, $S.avg_fps, $S.p95_ms, $S.p99_ms, $S.max_ms, $S.game_thread_avg_ms, $S.game_thread_p99_ms,
		$S.render_thread_avg_ms, $S.render_thread_p99_ms, $S.gpu_avg_ms, $S.gpu_p99_ms, $S.meets_target
	Copy-Item (Join-Path $Dir.FullName 'summary.json') (Join-Path $ProjectRoot "Documentation\PerfCaptures\$($Dir.Name).summary.json")
}
