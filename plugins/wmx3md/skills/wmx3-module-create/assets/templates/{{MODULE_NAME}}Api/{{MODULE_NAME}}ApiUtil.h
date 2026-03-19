/*******************************************************************************
*
* {{MODULE_NAME}}ApiUtil.h
*
* C++ API 유틸리티 함수 선언
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_LIB_UTIL_H
#define WMX3_{{MODULE_NAME_UPPER}}_LIB_UTIL_H

#include "WMX3OslIMDef.h"
#include "WMX3Api.h"
#include "WMX3ApiDef.h"
#include "{{MODULE_NAME}}Api.h"
#include "../include/{{MODULE_NAME}}ApiLocal.h"

namespace wmx3Api {

/* 오류 코드 변환: C API 오류코드 → C++ API 오류코드 */
int convert{{MODULE_NAME}}ErrorCode(int errCode);

/*
 * 여기에 C ↔ C++ 타입 변환 함수 선언 추가
 * 예:
 *   void convert{{MODULE_NAME}}DataCppToC(C_STRUCT_TYPE& dest, const {{MODULE_NAME}}CppType& src);
 *   void convert{{MODULE_NAME}}DataCToCpp({{MODULE_NAME}}CppType& dest, const C_STRUCT_TYPE& src);
 */

} /* namespace wmx3Api */

#endif
