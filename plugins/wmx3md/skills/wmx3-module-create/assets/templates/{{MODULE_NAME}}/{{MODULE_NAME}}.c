/*******************************************************************************
*
* {{MODULE_NAME}}.c
*
* Windows DLL 진입점 (Windows 전용)
* Linux에서는 빌드에서 제외됨
*
*******************************************************************************/

#include "{{MODULE_NAME}}.h"


/* DllMain은 반드시 TRUE를 반환해야 함 */
BOOL
OSL_API
DllMain(
        HINSTANCE hinstDLL,
        DWORD fdwReason,
        LPVOID lpvReserved
        )
{
    switch (fdwReason)
    {
        case DLL_PROCESS_ATTACH:
            /* DLL이 프로세스의 가상 주소 공간에 로드될 때 호출됨 */
            break;
        case DLL_PROCESS_DETACH:
            /* DLL이 프로세스에서 언로드될 때 호출됨 */
            break;
    }
    return TRUE;
}
