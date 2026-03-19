OSL_TYPE ?= rt

IM_REL ?= ../../../LmxInstallerFiles/lmx_im/releasefiles
ENG_REL ?= ../../../LmxInstallerFiles/lmx_engine/releasefiles
MOD_REL ?= ../../../LmxInstallerFiles/lmx_module/releasefiles
GCC_SUFFIX ?=

ifeq ($(OSL_TYPE), xeno)
	CFLAGS = -fPIC
else
	CFLAGS = -std=c++11 -fPIC
endif

INCLUDE = \
	-I ../include \
	-I $(IM_REL)/include \
	-I $(ENG_REL)/include \
	-I $(MOD_REL)/include

LIBRARY := \
	-L $(IM_REL)/lib -l imdll

TARGET = lib{{module_name}}api.a

OBJS = \
	{{MODULE_NAME}}Api.o \
	{{MODULE_NAME}}ApiTypes.o \
	{{MODULE_NAME}}ApiUtil.o \
	{{MODULE_NAME}}Api_ApiLog.o \
	{{MODULE_NAME}}Api_Event.o

SRCS = \
	{{MODULE_NAME}}Api.cpp \
	{{MODULE_NAME}}ApiTypes.cpp \
	{{MODULE_NAME}}ApiUtil.cpp \
	{{MODULE_NAME}}Api_ApiLog.cpp \
	{{MODULE_NAME}}Api_Event.cpp


all: $(OBJS)
	ar rcs $(TARGET) $^
	rm -f *.o

$(OBJS):$(SRCS)
	$(CROSS_COMPILE)gcc$(GCC_SUFFIX) -c $^ $(INCLUDE) $(LIBRARY) $(CFLAGS) $(EXTRA_OPTIONS) -Wno-write-strings

clean:
	$(RM) *.o *.a
