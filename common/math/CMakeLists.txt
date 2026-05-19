aux_source_directory(src Path_math)

add_library(math STATIC ${Path_math})

target_include_directories(math PUBLIC include)
target_link_libraries(math PUBLIC ${OpenCV_LIBS})
