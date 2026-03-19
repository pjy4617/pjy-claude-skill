/*******************************************************************************
*
* {{MODULE_NAME}}ApiUtil.cpp
*
* C++ API 유틸리티 함수 구현
* C++ 타입 ↔ C 타입 변환, 오류 코드 변환 등
*
*******************************************************************************/

#include "{{MODULE_NAME}}ApiUtil.h"

namespace wmx3Api {

/*------------------------------------------------------------------------------
 오류 코드 변환: C API 오류코드 → C++ API 오류코드
------------------------------------------------------------------------------*/
int convert{{MODULE_NAME}}ErrorCode(int errCode) {
    switch (errCode) {
    /*
     * 여기에 모듈 고유 오류 코드 변환 추가
     * 예:
     * case {{MODULE_NAME_UPPER}}_API_ERROR_SOME_ERROR:
     *     return {{MODULE_NAME}}ErrorCode::SomeError;
     */
    default:
        return ErrorCode::convertErrorCode(errCode);
    }
}

/*
 * 여기에 C 구조체 ↔ C++ 클래스 변환 함수 구현
 *
 * 패턴 예시:
 *
 * // C++ → C 변환 (API 호출 시 사용)
 * void convert{{MODULE_NAME}}DataCppToC(C_STRUCT_TYPE& dest, const {{MODULE_NAME}}CppType& src) {
 *     dest.someField = src.someField;
 *     // ...
 * }
 *
 * // C → C++ 변환 (상태 조회 시 사용)
 * void convert{{MODULE_NAME}}DataCToC pp({{MODULE_NAME}}CppType& dest, const C_STRUCT_TYPE& src) {
 *     dest.someField = src.someField;
 *     // ...
 * }
 */

} /* namespace wmx3Api */
