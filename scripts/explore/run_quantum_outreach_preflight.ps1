Param(
  [string]$Hdf5Path = "data/nist_completeblind.hdf5",
  [string]$ConvertConfig = "configs/nist_convert_config.json",
  [string]$EventsCsv = "data/nist_completeblind_side_streams.csv",
  [double]$StrictWindow = 0.25,
  [double]$StandardWindow = 15.0,
  [string]$BridgeJson = "artifacts/reports/ncc_singles_bridge_real.json",
  [string]$BridgePng = "artifacts/reports/ncc_singles_bridge_real.png",
  [string]$ChshJson = "battle_results/nist_round2_v2/ROUND2_chsh_result_parity.json",
  [string]$OutreachDir = "papers/open-review/outreach_quantum_pack"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/4] Convert HDF5 -> events CSV"
python "convert_nist_hdf5_to_events_csv.py" --hdf5 $Hdf5Path --config $ConvertConfig --output $EventsCsv
if ($LASTEXITCODE -ne 0) {
  if (Test-Path $EventsCsv) {
    Write-Warning "HDF5 conversion failed, but existing events CSV found. Continue with cached CSV: $EventsCsv"
  } else {
    throw "HDF5 conversion failed and no events CSV exists. Please install h5py or provide a valid CSV."
  }
}

Write-Host "[2/4] Build NCC singles/coincidences bridge report + figure"
python "scripts/explore/explore_ncc_singles_coincidence_bridge.py" --events-csv $EventsCsv --window-strict $StrictWindow --window-standard $StandardWindow --out-json $BridgeJson --out-png $BridgePng
if ($LASTEXITCODE -ne 0) {
  throw "NCC bridge generation failed."
}

Write-Host "[3/4] Generate outreach preflight package"
python "scripts/explore/generate_quantum_outreach_package.py" --ncc-json $BridgeJson --chsh-json $ChshJson --out-dir $OutreachDir
if ($LASTEXITCODE -ne 0) {
  throw "Outreach package generation failed."
}

Write-Host "[4/4] Done"
Write-Host "Bridge JSON: $BridgeJson"
Write-Host "Bridge PNG : $BridgePng"
Write-Host "Pack dir   : $OutreachDir"
