param([Parameter(Mandatory=$true)][string]$Jobs)
$ErrorActionPreference='Stop'
$jobPath=(Resolve-Path -LiteralPath $Jobs).Path
foreach ($name in [IO.File]::ReadAllLines($jobPath)) {
    $folder=Join-Path (Split-Path $jobPath -Parent) $name
    $stage=Join-Path $folder 'staging'
    $old=[IO.File]::ReadAllText((Join-Path $folder 'baseline.json')) | ConvertFrom-Json -AsHashtable
    $curr=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::Ordinal)
    foreach ($file in Get-ChildItem -LiteralPath $stage -Recurse -File) {
        $key=[IO.Path]::GetRelativePath($stage,$file.FullName).Replace('\','/')
        if ($key.EndsWith('.tmp',[StringComparison]::Ordinal)) { continue }
        $curr.Add($key,(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant())
    }
    $names=[Collections.Generic.SortedSet[string]]::new([StringComparer]::Ordinal)
    foreach ($key in $old.Keys) { [void]$names.Add($key) }
    foreach ($key in $curr.Keys) { [void]$names.Add($key) }
    $lines=[Collections.Generic.List[string]]::new()
    foreach ($key in $names) {
        if (-not $curr.ContainsKey($key)) { $lines.Add(('delete',$key,'-' -join [char]9)) }
        elseif (-not $old.Contains($key)) { $lines.Add(('add',$key,$curr[$key] -join [char]9)) }
        elseif ($old[$key] -cne $curr[$key]) { $lines.Add(('replace',$key,$curr[$key] -join [char]9)) }
    }
    $payload=if ($lines.Count) { ($lines -join [char]10) + [char]10 } else { '' }
    [IO.File]::WriteAllText((Join-Path $folder 'delta.tsv'),$payload,[Text.UTF8Encoding]::new($false))
}
