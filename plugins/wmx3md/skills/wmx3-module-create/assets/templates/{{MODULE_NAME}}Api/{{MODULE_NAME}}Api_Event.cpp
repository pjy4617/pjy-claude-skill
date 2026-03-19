/*******************************************************************************
*
* {{MODULE_NAME}}Api_Event.cpp
*
* 이벤트 C++ 래퍼 구현
* Event 모듈과의 연동을 위한 C++ 클래스 구현
*
*******************************************************************************/

#include "stdio.h"
#include "WMX3OslIMDef.h"
#include "IMDll.h"
#include "WMX3EngineDef.h"
#include "{{MODULE_NAME}}Api.h"
#include "{{MODULE_NAME}}ApiLocal.h"
#include "{{MODULE_NAME}}ApiPub.h"
#include "{{MODULE_NAME}}ApiUtil.h"
#include "WMX3ApiUtil.h"
#include "WMX3ApiDef.h"

/*
 * 여기에 이벤트 관련 C++ 클래스 구현
 *
 * 패턴 예시 (EventOutput 파생 클래스):
 *
 * wmx3Api::{{MODULE_NAME}}EventOutput::OutputFunctionArguments::OutputFunctionArguments()
 * {
 *     memset(this, 0x0, sizeof(OutputFunctionArguments));
 * }
 *
 * wmx3Api::{{MODULE_NAME}}EventOutput::{{MODULE_NAME}}EventOutput()
 *     : outputFunction(), output()
 * {
 * }
 *
 * int wmx3Api::{{MODULE_NAME}}EventOutput::GetOutputModuleId()
 * {
 *     return WMX3_MODULE_ID_{{MODULE_NAME_UPPER}};  // 실제 모듈 ID로 교체 필요
 * }
 *
 * WMX3APIFUNC wmx3Api::{{MODULE_NAME}}EventOutput::GetOutputData(unsigned char* buff, int buffSize, int* dataSize)
 * {
 *     if (buff == NULL) return ErrorCode::ArgumentIsNull;
 *     if (buffSize < sizeof(이벤트_출력_데이터_타입)) return ErrorCode::ArgumentOutOfRange;
 *
 *     // 여기에 C++ → C 변환 로직 구현
 *     // ...
 *
 *     if (dataSize != NULL) *dataSize = sizeof(이벤트_출력_데이터_타입);
 *     return ErrorCode::None;
 * }
 *
 * WMX3APIFUNC wmx3Api::{{MODULE_NAME}}EventOutput::SetOutputData(int moduleId, unsigned char* data, int dataSize)
 * {
 *     if (data == NULL) return ErrorCode::ArgumentIsNull;
 *     if (dataSize != sizeof(이벤트_출력_데이터_타입)) return ErrorCode::ArgumentOutOfRange;
 *
 *     // 여기에 C → C++ 변환 로직 구현
 *     // ...
 *
 *     return ErrorCode::None;
 * }
 */
