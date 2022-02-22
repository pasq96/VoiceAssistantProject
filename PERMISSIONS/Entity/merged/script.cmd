
del mergeEntities.yml

for %%I in (..\*.yml) do (
    type "%%I" >> merged.tmp
    timeout 0.5 >nul
    echo. >> merged.tmp
    echo. >> merged.tmp
)

move merged.tmp mergeEntities.yml