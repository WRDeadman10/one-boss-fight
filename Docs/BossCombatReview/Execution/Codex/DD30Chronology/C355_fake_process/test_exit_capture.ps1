. (Join-Path (Split-Path -Parent $PSScriptRoot) 'run_chronology_v2.ps1') -FunctionsOnly
$rows=@()
foreach($expected in @(0,3)){
 $script=Join-Path $PSScriptRoot "exit$expected.ps1"
 $result=Invoke-CachedHandleProcess -FilePath (Get-Command powershell).Source -Arguments @('-NoProfile','-ExecutionPolicy','Bypass','-File',$script) -TimeoutSeconds 15 -StdoutPath (Join-Path $PSScriptRoot "exit${expected}_stdout.log") -StderrPath (Join-Path $PSScriptRoot "exit${expected}_stderr.log")
 if($null -eq $result.exit_code -or $result.exit_code -ne $expected -or $result.timed_out){throw "FAIL expected $expected got $($result.exit_code)"}
 $rows+=$result
 Write-Output "FAKE_PROCESS expected=$expected actual=$($result.exit_code) outcome=$($result.outcome) cached_handle=$($result.cached_handle)"
}
$rows | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'observed_exit_codes.json') -Encoding utf8
Write-Output 'PASS fake-process codes0and3; no Unreal process, not UE test evidence'
