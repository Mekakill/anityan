cmake_minimum_required(VERSION 3.18)
project(kuni VERSION 1.0.0)

option(BUILD_SHARED_LIBS OFF)

set(AUI_VERSION b5186aaf5f78ad6756c04aad3992ac8d3a07d319)

# Use AUI.Boot
file(
        DOWNLOAD
        https://raw.githubusercontent.com/aui-framework/aui/7aac4a2b15238bbf7d25fcf029e914dbc1f02413/aui.boot.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/aui.boot.cmake)
include(${CMAKE_CURRENT_BINARY_DIR}/aui.boot.cmake)

set(AUI_COROUTINES "Use C++20 coroutines" ON)
auib_mark_var_forwardable(AUI_COROUTINES)

# import AUI
auib_import(aui https://github.com/aui-framework/aui
        COMPONENTS core json curl crypt image views
        VERSION ${AUI_VERSION})


auib_import(date https://github.com/HowardHinnant/date)

set(AUIB_TD_VALIDATE OFF)
auib_import(Td https://github.com/tdlib/td
        VERSION 0ae923c)

aui_executable(${PROJECT_NAME})

target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/secrets)

# Link required libs
aui_link(${PROJECT_NAME} PUBLIC aui::core aui::json aui::curl aui::crypt aui::image aui::views Td::TdStatic)

aui_enable_tests(${PROJECT_NAME})
