/*******************************************************************************
*
* {{MODULE_NAME}}Api.h
*
* C++ API 클래스 헤더 - wmx3Api 네임스페이스
* {{MODULE_NAME}} 모듈 API 함수 선언 및 데이터 타입 정의
*
*******************************************************************************/

#ifndef WMX3_{{MODULE_NAME_UPPER}}_API_H
#define WMX3_{{MODULE_NAME_UPPER}}_API_H
#include "WMX3Api.h"


namespace wmx3Api{

    namespace constants {
        /* 여기에 {{MODULE_NAME}} 모듈 관련 상수 정의 */
        /* 예: static const int max{{MODULE_NAME}}Channel = 255; */
    }

    /* {{MODULE_NAME}} 모듈 오류 코드 클래스 */
    class {{MODULE_NAME}}ErrorCode : public ErrorCode{
    public:
        enum {
            /* 여기에 모듈 고유 오류 코드 열거형 정의 */
            /* 예: InvalidBuffControl = 0x000XX000, */
        };
    };

    /* {{MODULE_NAME}} 모듈 상태 열거형 */
    class {{MODULE_NAME}}State {
    public:
        enum T {
            /* 여기에 모듈 상태 열거형 정의 */
            /* 예: Idle, Active, Stop, ... */
        };
    };

    /* {{MODULE_NAME}} 모듈 상태 구조체 */
    class {{MODULE_NAME}}Status {
    public:
        {{MODULE_NAME}}Status();
        /* 여기에 상태 필드 정의 */
        /* 예: {{MODULE_NAME}}State::T state; */
    };

    /* {{MODULE_NAME}} C++ API 클래스 */
    class {{MODULE_NAME}} {
    private:
        WMX3Api *wmx3Api;
        int statChnlId;
        bool isSelfDev;
        void init(WMX3Api *f);
        void close();
    public:
        {{MODULE_NAME}}(WMX3Api *f);
        {{MODULE_NAME}}(const {{MODULE_NAME}}& src);
        {{MODULE_NAME}}& operator=(const {{MODULE_NAME}}& src);
        {{MODULE_NAME}}();
        ~{{MODULE_NAME}}();

        /* 오류 코드를 문자열로 변환 */
        static WMX3APIFUNC ErrorToString(int errCode, char *pString, unsigned int size);
        static WMX3APIFUNC ErrorToString(int errCode, wchar_t *pString, unsigned int size);

        /* API 로그를 문자열로 변환 */
        static WMX3APIFUNC ApiLogToString(unsigned char* pLogData, unsigned int logDataSize, char *pString, unsigned int size);
        static WMX3APIFUNC ApiLogToString(unsigned char* pLogData, unsigned int logDataSize, wchar_t *pString, unsigned int size);

        /* 라이브러리 버전 조회 */
        static WMX3APIFUNC GetLibVersion(int *pMajorVersion, int *pMinorVersion, int *pRevisionVersion, int *pFixVersion);

        /* 디바이스 유효성 확인 */
        bool IsDeviceValid();

        /* 모듈 버전 조회 */
        WMX3APIFUNC GetVersion(int *pMajorVersion, int *pMinorVersion, int *pRevisionVersion, int *pFixVersion);

        /* 상태 조회 */
        WMX3APIFUNC GetStatus({{MODULE_NAME}}Status* pStatus);

        /*
         * 여기에 모듈 고유 API 함수 선언 추가
         * 예:
         *   WMX3APIFUNC DoSomething(int param);
         *   WMX3APIFUNC GetData({{MODULE_NAME}}Status* pStatus);
         */
    };


}

#endif
