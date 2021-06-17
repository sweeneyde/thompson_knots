In these files, elements of Thompson's group F
(pairs of trees represented by Dyck words)
are partitioned by the HOMFLYPT polynomial of the link that they produce.

Since HOMFLYPT polynomials are a property of oriented links
and Thompson's group does not in general offer a canonical orientation,
orientations have been assigned arbitrarily.
Hence, there are multiple polynomials per unoriented link,
and there might not be the same number of tree pairs in each polynomial component.

`unoriented6_labelled.txt` and `unoriented7.txt` have each polynomial component labelled with the name of the corresponding link. I added these labels by hand, so it's possible there are mistakes.

To save space and computation time,
`unoriented10_prime_and_first_of_symmetries.txt`
does only includes tree-pairs which are ["coprime"](http://oeis.org/A335729),
since any sub-diagram will give a connected sum of two links.
Another reduction made is to only include one of each of the four
reflections of any tree-pair. This file can thus only be relied on
to find the *prime* links with thompson index at most 10.
