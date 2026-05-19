aux_source_directory(src Path_A2)

add_library(A2 STATIC ${Path_A2})

target_include_directories(A2 PUBLIC include)
# 解决 A2.h 中 size_t 未定义的问题：在编译 A2 时强制预包含 <cstddef>
target_compile_options(A2 PRIVATE -include cstddef)
