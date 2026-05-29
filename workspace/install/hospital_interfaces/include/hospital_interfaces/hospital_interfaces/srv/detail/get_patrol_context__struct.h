// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hospital_interfaces:srv/GetPatrolContext.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__STRUCT_H_
#define HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/GetPatrolContext in the package hospital_interfaces.
typedef struct hospital_interfaces__srv__GetPatrolContext_Request
{
  uint8_t structure_needs_at_least_one_member;
} hospital_interfaces__srv__GetPatrolContext_Request;

// Struct for a sequence of hospital_interfaces__srv__GetPatrolContext_Request.
typedef struct hospital_interfaces__srv__GetPatrolContext_Request__Sequence
{
  hospital_interfaces__srv__GetPatrolContext_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__srv__GetPatrolContext_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'global_context'
// Member 'final_summary'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/GetPatrolContext in the package hospital_interfaces.
typedef struct hospital_interfaces__srv__GetPatrolContext_Response
{
  bool success;
  rosidl_runtime_c__String global_context;
  rosidl_runtime_c__String final_summary;
} hospital_interfaces__srv__GetPatrolContext_Response;

// Struct for a sequence of hospital_interfaces__srv__GetPatrolContext_Response.
typedef struct hospital_interfaces__srv__GetPatrolContext_Response__Sequence
{
  hospital_interfaces__srv__GetPatrolContext_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__srv__GetPatrolContext_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__GET_PATROL_CONTEXT__STRUCT_H_
