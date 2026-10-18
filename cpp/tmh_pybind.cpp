
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "bitstream_random.hpp"
#include "weighted_minwise_hashing.hpp"
#include <cstdint>
#include <vector>
#include <utility>

namespace py = pybind11;

namespace {

constexpr uint64_t DEFAULT_SEED = 0x123456789ABCDEF0ULL;

class RNGFunction {
  const uint64_t seed;
public:
  typedef tmh::WyrandBitStream RngType;

  RNGFunction(uint64_t seed) : seed(seed) {}

  tmh::WyrandBitStream operator()(uint64_t x) const {
    return tmh::WyrandBitStream(x, seed);
  }

  tmh::WyrandBitStream operator()(uint64_t x, uint64_t y) const {
    return tmh::WyrandBitStream(x, y, seed);
  }
};

inline uint64_t pack_shorts(uint16_t x, uint16_t y) {
    return (static_cast<uint64_t>(x) << 16) | static_cast<uint64_t>(y);
}

} 
std::vector<std::pair<uint64_t, double>> build_signature_from_cms(
    py::array_t<double, py::array::c_style | py::array::forcecast> table,
    uint32_t num_hashes,
    uint64_t seed = DEFAULT_SEED) {

    auto buf = table.unchecked<2>();
    ssize_t depth = buf.shape(0);
    ssize_t width = buf.shape(1);

    std::vector<std::pair<uint64_t, double>> flattened;
    flattened.reserve(depth * width);

    for (ssize_t row = 0; row < depth; ++row) {
        for (ssize_t col = 0; col < width; ++col) {
            double value = buf(row, col);
            if (value != 0.0) {
                uint64_t id = pack_shorts(static_cast<uint16_t>(row), static_cast<uint16_t>(col));
                flattened.emplace_back(id, value);
            }
        }
    }

    tmh::TreeMinHash<RNGFunction> hasher(num_hashes, RNGFunction(seed));
    return hasher(flattened);
}


// std::vector<std::pair<uint64_t, double>> build_signature(
//     const std::vector<std::pair<uint64_t, double>>& flattened,
//     uint32_t num_hashes,
//     uint64_t seed = DEFAULT_SEED) {

//     tmh::TreeMinHash<RNGFunction> hasher(num_hashes, RNGFunction(seed));
//     return hasher(flattened);
// }

PYBIND11_MODULE(tmh_pybind, m) {
    m.doc() = "Python bindings for TreeMinHash (weighted minwise hashing)";

    // m.def("pack_shorts",
    //       [](uint16_t row, uint16_t col) { return pack_shorts(row, col); },
    //       py::arg("row"), py::arg("col"),
    //       "Pack a (row, col) CMS cell coordinate into a 64-bit id, "
    //       "matching tmhsketches_cms.cpp's id scheme.");

    m.def("build_signature_from_cms", &build_signature_from_cms,
          py::arg("table"), py::arg("num_hashes"), py::arg("seed") = DEFAULT_SEED,
          "Flatten a (depth x width) CMS matrix and build a weighted "
          "TreeMinHash signature from it. Returns a list of (id, value) "
          "pairs of length num_hashes.");

    // m.def("build_signature", &build_signature,
    //       py::arg("flattened"), py::arg("num_hashes"), py::arg("seed") = DEFAULT_SEED,
    //       "Build a weighted TreeMinHash signature from a list of "
    //       "(id, weight) pairs. Returns a list of (id, value) pairs of "
    //       "length num_hashes.");
}
