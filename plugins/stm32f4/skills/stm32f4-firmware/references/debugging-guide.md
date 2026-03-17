# STM32F4 Debugging Guide

## 1. HardFault 분석

HardFault는 가장 흔한 크래시 원인이다. 디버거 없이도 원인을 좁힐 수 있다.

### HardFault Handler에서 레지스터 덤프
```c
void HardFault_Handler(void)
{
    __asm volatile (
        "TST lr, #4       \n"
        "ITE EQ           \n"
        "MRSEQ r0, MSP    \n"
        "MRSNE r0, PSP    \n"
        "B HardFault_Handler_C \n"
    );
}

void HardFault_Handler_C(uint32_t *stack)
{
    volatile uint32_t r0  = stack[0];
    volatile uint32_t r1  = stack[1];
    volatile uint32_t r2  = stack[2];
    volatile uint32_t r3  = stack[3];
    volatile uint32_t r12 = stack[4];
    volatile uint32_t lr  = stack[5];   /* 호출자 복귀 주소 */
    volatile uint32_t pc  = stack[6];   /* 폴트 발생 주소 ← 핵심 */
    volatile uint32_t psr = stack[7];

    volatile uint32_t cfsr = SCB->CFSR;  /* Configurable Fault Status */
    volatile uint32_t hfsr = SCB->HFSR;  /* HardFault Status */
    volatile uint32_t mmfar = SCB->MMFAR; /* MemManage Fault Address */
    volatile uint32_t bfar = SCB->BFAR;  /* BusFault Address */

    (void)r0; (void)r1; (void)r2; (void)r3;
    (void)r12; (void)lr; (void)pc; (void)psr;
    (void)cfsr; (void)hfsr; (void)mmfar; (void)bfar;

    __BKPT(0);  /* 디버거에서 여기서 멈추면 위 변수들을 확인 */
    while (1) {}
}
```

### CFSR 비트 해석
| 비트 | 이름 | 의미 |
|------|------|------|
| [0] IACCVIOL | Instruction Access Violation | 실행 불가 영역에서 코드 실행 시도 |
| [1] DACCVIOL | Data Access Violation | 접근 불가 영역 읽기/쓰기 |
| [8] IBUSERR | Instruction Bus Error | Flash/외부 메모리 읽기 오류 |
| [9] PRECISERR | Precise Data Bus Error | BFAR에 정확한 주소 기록됨 |
| [16] UNDEFINSTR | Undefined Instruction | 잘못된 함수 포인터, 스택 오버플로우 |
| [17] INVSTATE | Invalid State | Thumb 비트 미설정 (함수 포인터 주소 홀수 확인) |
| [18] INVPC | Invalid PC | 올바르지 않은 EXC_RETURN 값 |

### 흔한 원인과 대처
- **PC가 0x00000000 근처**: NULL 함수 포인터 호출
- **PC가 Flash 범위 밖**: 스택 오버플로우로 복귀 주소 손상
- **UNDEFINSTR**: .thumb_func 누락 또는 포인터 LSB=0
- **DACCVIOL + MMFAR**: 해당 주소 접근 권한 확인

## 2. Printf 리다이렉션

### 방법 A: SWO/ITM (디버거 필요, UART 핀 불필요)
```c
// SWO 출력 (PB3 또는 전용 SWO 핀)
int _write(int file, char *data, int len)
{
    for (int i = 0; i < len; i++) {
        ITM_SendChar(data[i]);
    }
    return len;
}
```
OpenOCD에서 SWO 캡처:
```
openocd -f openocd.cfg -c "tpiu config internal swo.log uart false 168000000"
```

### 방법 B: UART 리다이렉션
```c
// USART2 사용 (PA2=TX)
int _write(int file, char *data, int len)
{
    HAL_UART_Transmit(&huart2, (uint8_t *)data, len, HAL_MAX_DELAY);
    return len;
}
```
`-specs=nano.specs` 사용 시 `_write` 심볼이 libc에서 호출된다. 링커에 `-u _printf_float`을 추가하면 float 출력도 가능 (코드 크기 증가).

### 방법 C: Semihosting (개발 전용, 매우 느림)
```bash
# 링커 플래그: -specs=rdimon.specs -lc -lrdimon
# OpenOCD: monitor arm semihosting enable
```
프로덕션에서 절대 사용 금지 — 디버거 미연결 시 HardFault 발생.

## 3. GDB 디버깅 팁

### 기본 연결
```bash
arm-none-eabi-gdb build/firmware.elf
(gdb) target remote :3333
(gdb) monitor reset halt
(gdb) load
(gdb) break main
(gdb) continue
```

### 유용한 GDB 명령
```
info registers           # 레지스터 전체 보기
x/20xw 0x20000000       # SRAM 시작 20워드 헥스 덤프
print/x SCB->CFSR       # CFSR 레지스터 값
bt                       # 백트레이스 (콜스택)
watch *0x20000100        # 해당 주소 변경 감시 (하드웨어 워치포인트)
set var s_appState = 0   # 변수 강제 변경
```

### .gdbinit 자동 설정
```
target remote :3333
monitor reset halt
load
break main
continue
```

## 4. SWD 연결 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| "No target connected" | SWD 배선 오류, VDD 미인가 | 배선 확인, 3.3V 확인 |
| "Target voltage too low" | 전원 불안정 | 디커플링 캐패시터 확인 |
| "Cannot halt target" | 코드가 SWD 핀을 GPIO로 전환 | BOOT0=1로 시스템 부팅 후 Erase |
| "Flash write failed" | Flash 보호(RDP/WRP) 활성 | Option Bytes에서 보호 해제 |

BOOT0=1 (시스템 메모리 부팅)로 SWD 복구:
```bash
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
  -c "init; reset halt; stm32f4x mass_erase 0; reset run; exit"
```

## 5. 스택 오버플로우 감지

### 패턴: 스택 워터마크
```c
// 링커 스크립트에서 스택 시작 주소 가져오기
extern uint32_t _estack;
extern uint32_t _Min_Stack_Size;

// 초기화 시 스택 영역을 패턴으로 채우기
#define STACK_FILL_PATTERN 0xDEADBEEF
void Stack_FillPattern(void)
{
    uint32_t *stackBottom = (uint32_t *)((uint32_t)&_estack - (uint32_t)&_Min_Stack_Size);
    uint32_t *sp;
    __asm volatile("MOV %0, SP" : "=r"(sp));
    for (uint32_t *p = stackBottom; p < sp - 8; p++) {
        *p = STACK_FILL_PATTERN;
    }
}

// 주기적으로 최소 여유 확인
uint32_t Stack_GetFreeBytes(void)
{
    uint32_t *stackBottom = (uint32_t *)((uint32_t)&_estack - (uint32_t)&_Min_Stack_Size);
    uint32_t *p = stackBottom;
    while (*p == STACK_FILL_PATTERN && p < (uint32_t *)&_estack) p++;
    return (uint32_t)p - (uint32_t)stackBottom;
}
```
