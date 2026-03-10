// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from play_motion2_msgs:srv/GetMotionInfo.idl
// generated code does not contain a copyright notice

#ifndef PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__STRUCT_H_
#define PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'motion_key'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/GetMotionInfo in the package play_motion2_msgs.
typedef struct play_motion2_msgs__srv__GetMotionInfo_Request
{
  rosidl_runtime_c__String motion_key;
} play_motion2_msgs__srv__GetMotionInfo_Request;

// Struct for a sequence of play_motion2_msgs__srv__GetMotionInfo_Request.
typedef struct play_motion2_msgs__srv__GetMotionInfo_Request__Sequence
{
  play_motion2_msgs__srv__GetMotionInfo_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} play_motion2_msgs__srv__GetMotionInfo_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'motion'
#include "play_motion2_msgs/msg/detail/motion__struct.h"

/// Struct defined in srv/GetMotionInfo in the package play_motion2_msgs.
typedef struct play_motion2_msgs__srv__GetMotionInfo_Response
{
  play_motion2_msgs__msg__Motion motion;
} play_motion2_msgs__srv__GetMotionInfo_Response;

// Struct for a sequence of play_motion2_msgs__srv__GetMotionInfo_Response.
typedef struct play_motion2_msgs__srv__GetMotionInfo_Response__Sequence
{
  play_motion2_msgs__srv__GetMotionInfo_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} play_motion2_msgs__srv__GetMotionInfo_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PLAY_MOTION2_MSGS__SRV__DETAIL__GET_MOTION_INFO__STRUCT_H_
