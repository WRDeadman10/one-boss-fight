$ErrorActionPreference='Stop'
$r=$PSScriptRoot
python -I "$r\capture_state.py" pre
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
python -I "$r\verify_pins.py"
exit $LASTEXITCODE
