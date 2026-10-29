# DD24 C281 test collection mutation review

Exhaustive Add/AddUnique/Insert/Append/Emplace/SetNum scan:19 call sites (array_mutation_inventory.txt).
Owned Result.Add(C): C comes from owner component set, not Result.
Cases.Add at148-160:13 newly constructed FBad records, lambdas capture no Cases/array element reference.
Cases.Add at178-180:3 new FBad records; each captures a by-value copied external FSoftObjectPath, then assigns a scalar montage field. No container mutation in those lambdas.
Definition D->Fields.Add(Field) at202: Field is an independent stack record, not from D->Fields.
Valid.Add(Repeated) at261: Repeated is a separate stack config. The three equal montage pointers are scalar fields, not array elements; sharing the asset identity is intentionally legal.
No Insert/Append/Emplace/SetNum or same-array source-element argument exists in this test file. No Add(R.Array[index]) or reference local or MoveTemp array element. No changed fixture can reproduce the DD23 self-alias operation.
This is source reasoning, not a compiler/Unreal test. Native components are never begun/ticked/applied; plain begun owner receives component afterwards.
