# DD25 source-only collection-mutation review

Every Add/AddUnique/Insert/Append/Emplace/SetNum site is listed in array_mutation_inventory.txt.
Owned Result.Add(C) reads the distinct owner component collection.
Cases.Add constructs new FBad records with no reference to Cases or its elements.
The two malformed-path Cases.Add sites capture a copied external FSoftObjectPath and assign scalar soft references, not a container element.
Definition D->Fields.Add(Field) copies a distinct stack FRPGParityField.
Seven Valid.Add(R) sites copy separate scoped stack records before iteration begins. Neither the validator/configure loop nor callbacks mutate Valid.
FRuntime Counters is initializer-built from getter return values and never appended to.
There is no Insert/Append/Emplace/SetNum, Add(R.Array[index]), Add(array reference local), MoveTemp(array element), or self-array source argument in the test source. No runtime/UE proof is claimed by this manual provenance audit.
