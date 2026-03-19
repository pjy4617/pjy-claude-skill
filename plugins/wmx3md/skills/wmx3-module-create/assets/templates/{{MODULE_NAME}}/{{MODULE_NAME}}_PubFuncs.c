/*******************************************************************************
*
* {{MODULE_NAME}}_PubFuncs.c
*
* 퍼블릭 함수 구현
* {{MODULE_NAME}}ApiPub.h를 통해 다른 RT 모듈에서 접근 가능한 함수들
*
*******************************************************************************/

#include "{{MODULE_NAME}}.h"
#include "{{MODULE_NAME}}_PubFuncs.h"
#include "{{MODULE_NAME}}_Util.h"

/* 전역 데이터 참조 (퍼블릭 함수에서 사용) */
extern {{MODULE_NAME_UPPER}}_DATA __{{MODULE_NAME}}Data__;

/*
 * 여기에 퍼블릭 함수 구현
 *
 * 패턴 예시 (채널 기반 제어 함수):
 *
 * int __stdcall {{MODULE_NAME}}DoSomethingFunc(int channel) {
 *     P{{MODULE_NAME_UPPER}}_DATA p{{MODULE_NAME}}Data = &__{{MODULE_NAME}}Data__;
 *
 *     // 파라미터 유효성 검사
 *     if (p{{MODULE_NAME}}Data->someField == NULL) {
 *         return {{MODULE_NAME_UPPER}}_PUB_ERROR_INVALID_DATA;
 *     }
 *     if (channel < 0 || channel >= {{MODULE_NAME_UPPER}}_PUB_MAX_CHANNEL) {
 *         return {{MODULE_NAME_UPPER}}_PUB_ERROR_INVALID_CHANNEL;
 *     }
 *
 *     // 이전 설정 적용 중 체크
 *     if (이전_설정_적용_중) {
 *         return {{MODULE_NAME_UPPER}}_PUB_ERROR_PREVIOUS_SETTINGS_BEING_APPLIED;
 *     }
 *
 *     // 여기에 실제 처리 로직 구현
 *
 *     return {{MODULE_NAME_UPPER}}_PUB_ERROR_NONE;
 * }
 */
