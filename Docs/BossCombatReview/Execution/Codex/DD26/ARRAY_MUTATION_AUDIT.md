# DD26 changed-code collection mutation review

changed_array_mutations.json is the exhaustive changed-test-line Add/AddUnique/Insert/Append/Emplace/SetNum inventory, seven sites. Each is Plans.Add(Make...Plan()) in the pre-existing HydrationPreparation RequiredPaths helper. Every argument is a fresh factory return value, no reference to Plans or any of its elements. This helper was factory-derived before DD26; it is NOT one of the six independently literal-written AllRequiredPaths lists.

The six new field expectation blocks and expected class/name arrays are independent literal initializer additions, not Add of any container element. New prefix/suffix assertions and all-later-name loops read existing arrays only. The fault Ordinals array is immutable; the loop consumes values, it does not insert into Ordinals. No new Insert/Append/Emplace/SetNum or reference/MoveTemp argument aliases its own destination. Existing collection mutations not changed retain their earlier provenance; no runtime claim is made.

Production MakeBossCorePlans appends seven fresh factory returns to Plans; ManagedCoreConsumerClasses returns class literals. Neither references its own array elements. No callback is run in the preflight. This is manual source reasoning, not C++/UE validation.
