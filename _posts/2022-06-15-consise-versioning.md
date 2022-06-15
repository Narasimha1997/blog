---
title: Concise 24-bit encoding of Semantic versions
published: true
---
Recently I built a proof-of-concept [decentralized package manager for python](https://github.com/Narasimha1997/dipmp) compatible with PIP - which uses IPFS for storing python package wheels and Ethereum smart contract (written in solidity) for storing the indexes. One of the challenges while creating an index as a solidity smart contract was to find out a way to store and compare versions of the same package efficiently, python packages are versioned according to [semantic versioning scheme (symver)](https://semver.org/), for example `aio-eth-1.2.4` is a a valid python package with version `1.2.4`, the trivial way to store this version is to use solidity `string` data-type, however comparing strings is not efficient in solidity and there is no direct way of doing it. Basically this is how the index structure implemented using solidity looks like:

```solidity
// represents a stored package
struct PackageIdentity {
    string IPFSHash;
    string idata;
    address by;
    uint24 version;
}

// maps (package => (version => identity))
mapping(string => mapping(uint8 => PackageIdentity)) packages;

// stores mapping counts (allow only 256 versions to be present)
mapping(string => uint8) version_counts;
```
We have a mapping called `packages` which associates package names with a nested mapping that can store upto 256 entries of the same package with different versions, these entries are stored sequentially startng from index `0` to `255` (since we are using `uint8`) - this behaves more or less like a dynamically sized array. Since we can't tell how many entries are there for each package, we maintain another mapping called `version_counts`, which associates each package present in `packages` mapping with a `uint8` telling how many different version entries are present for that package (it acts as an upper bound, since we keep track of this number, we can get a list of different versions of the same package by iterating over `packages` mapping like `packages[name][0]...packages[name][count-1]`, here count is obtained from `version_counts` mapping). 

Each entry is of type `PackageIdentity`, this `struct` has fields like `IPFSHash` which can be used to obtain the wheel file from IPFS, along with that we are also storing `idata` which is nothing but the original file name of the wheel fine, the `by` field contains the address of the owner who pushed the given version of the package. The interesting field here is `version` which is a `uint24` field (24-bit unsigned integer) - this field contains the numeric representation of semantic version. Using a numeric type instead of `uint24` can speed up many operations, for example, here is a function that checks whether a given package exists or not everytime someone tries to push a new (package, version):

```solidity
function checkExists(string memory name, uint24 version) external view returns(bool) {
    uint8 count = version_counts[name];
    for (uint8 i = 0; i < count; i++) {
        if (packages[name][i].version == version) {
            return true;
        }
    }
    return false;
}
```
In this loop, we obtian the current count of package entries for the given package and use it as an upper bound to iterate over each package entry and check the equality of the version, using a numeric type will allow us to compare two entities like numbers than as a string, thus we eleliminate the need for using O(N) string comparisions.

### Encoding and decoding of semantic versions
We saw why we need numeric types for representating semantic versions, but there are many ways by which a string can be interpreted like a number. One naive way of doing that is to just obtain the underlying bytes representation of a string (since string is a sequence of characters), i.e string `1.2.3` can be represented as  `312e322e33` in hex, this is same as `211228438067` numerically, while this seems fine, it suffers from two major drawbacks:
1. There is no fixed size - the numeric representation can result in any arbitrary large number of any size, it is hard to decide the limits.
2. Wastage of storage space - To overcome (1), we can choose a large enough numeric type like `uint128` or `uint256` which can easily result in allocating lot of redundant space, Ethereum blockchain has limitations on the storage space used by variables, thus we have to be judicious about the wastage of storage space.

To overcome these limitations, we can design a 24-bit encoding scheme, as we know semantic version is a combination of three parts (separated by a '.'), we can assume one byte per part, therefore each part can hold number between `0-255`, even if we impose this restriction we can still have `256*256*256 = 16777216` unique versions per package, which is beyond practical possibilities. Encoding of decoding of semantic versions into this representation is trivial, we take each part (split at `.`), convert the number to int and we pack these numbers into one 24-bit number (part 1 occupies 0-7 bits, part 2 occupies 8-15 bits and part-3 occupies 16-23 bits of a 24-bit number), while decoding we do the exact reverse operation. Here is a fucntion to encode (in python):

```python
def encode(version_string):
    version = version_string.split(".")
    v = 0
    for idx, split in enumerate(version):
        if int(split) > 255:
            return 0
        v = v | (int(split) << (24 - (idx + 1) * 8))
    return v

# test
print(encode('1.2.3'))
print(encode('255.255.2'))

# output:
# 66051
# 16776962
```
Decoder does exactly opposite, here is the snippet for decoder:
```python
def decode(version):
    c1 = (version >> 16) & 0xff
    c2 = (version >> 8) & 0xff
    c3 = version & 0xff

    return "{}.{}.{}".format(c1, c2, c3)

print(decode(66051))
print(decode(16776962))

# output:
# 1.2.3
# 255.255.2
```
If we want to make space for more versions, we can use 64-bit number instead of 24-bit and use 16 bits per part (and wasting 2-bytes at last). Since encoding and decoding operations are interpreted by the application layer and the smart-contract has nothing to do with it, we can do this operation completely off-chain. Thus we can concisely encode semantic versions for efficient storage and quick comparisions on blockchain.
