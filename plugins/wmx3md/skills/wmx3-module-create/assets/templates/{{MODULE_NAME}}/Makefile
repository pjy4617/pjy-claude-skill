#==============================================================================
# Makefile - {{MODULE_NAME}} Core RTDLL 레거시 Linux 빌드
#==============================================================================

# OSL 타입: rt (표준) 또는 xeno (Xenomai)
OSL_TYPE ?= rt

# 릴리즈 파일 경로 (환경변수 또는 상대경로 사용)
IM_REL  ?= ../../LmxInstallerFiles/lmx_im/releasefiles
ENG_REL ?= ../../LmxInstallerFiles/lmx_engine/releasefiles
MOD_REL ?= ../../LmxInstallerFiles/lmx_module/releasefiles
OSL_REL ?= ../../LmxInstallerFiles/lmx_osl/releasefiles

# 크로스 컴파일 지원
CROSS_COMPILE ?=
GCC_SUFFIX    ?=

# 컴파일러 설정
ifeq ($(OSL_TYPE), xeno)
    CC = $(shell xeno-config --cc)
else
    CC = $(CROSS_COMPILE)gcc$(GCC_SUFFIX)
endif

# 출력 파일명 (Linux 소문자_언더스코어 관례)
TARGET = {{module_name_snake}}.so

# 소스 파일 목록
SRCS = \
    {{MODULE_NAME}}_Event.c \
    {{MODULE_NAME}}_Funcs.c \
    {{MODULE_NAME}}_Motion.c \
    {{MODULE_NAME}}_PubFuncs.c \
    {{MODULE_NAME}}_Util.c

OBJS = $(SRCS:.c=.o)

# 인클루드 경로
INCLUDES = \
    -I../include \
    -I$(IM_REL)/include \
    -I$(ENG_REL)/include \
    -I$(MOD_REL)/include

# 컴파일 플래그
CFLAGS = -fPIC -Wno-format-truncation $(EXTRA_OPTIONS)

ifeq ($(OSL_TYPE), xeno)
    XENO_CFLAGS  = $(shell xeno-config --alchemy --posix --cflags)
    XENO_LDFLAGS = $(shell xeno-config --alchemy --posix --ldflags --auto-init-solib)
    CFLAGS += $(XENO_CFLAGS)
endif

# 링크 플래그
LDFLAGS = \
    -shared \
    -Wl,--version-script=export \
    -Wl,--no-undefined \
    -L$(OSL_REL)/lib \
    -L$(IM_REL)/lib \
    -losl -limlib \
    -ldl -lpthread -lrt -lm

ifeq ($(OSL_TYPE), xeno)
    LDFLAGS += $(XENO_LDFLAGS)
endif

# 빌드 규칙
.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)
	strip $@

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
