// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hospital_interfaces:action/GenerateReport.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__STRUCT_H_
#define HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'folder_path'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_Goal
{
  rosidl_runtime_c__String folder_path;
} hospital_interfaces__action__GenerateReport_Goal;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_Goal.
typedef struct hospital_interfaces__action__GenerateReport_Goal__Sequence
{
  hospital_interfaces__action__GenerateReport_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'final_report'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_Result
{
  bool success;
  rosidl_runtime_c__String final_report;
} hospital_interfaces__action__GenerateReport_Result;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_Result.
typedef struct hospital_interfaces__action__GenerateReport_Result__Sequence
{
  hospital_interfaces__action__GenerateReport_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'current_zone'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_Feedback
{
  rosidl_runtime_c__String current_zone;
  float percentage_complete;
} hospital_interfaces__action__GenerateReport_Feedback;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_Feedback.
typedef struct hospital_interfaces__action__GenerateReport_Feedback__Sequence
{
  hospital_interfaces__action__GenerateReport_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "hospital_interfaces/action/detail/generate_report__struct.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  hospital_interfaces__action__GenerateReport_Goal goal;
} hospital_interfaces__action__GenerateReport_SendGoal_Request;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_SendGoal_Request.
typedef struct hospital_interfaces__action__GenerateReport_SendGoal_Request__Sequence
{
  hospital_interfaces__action__GenerateReport_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} hospital_interfaces__action__GenerateReport_SendGoal_Response;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_SendGoal_Response.
typedef struct hospital_interfaces__action__GenerateReport_SendGoal_Response__Sequence
{
  hospital_interfaces__action__GenerateReport_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} hospital_interfaces__action__GenerateReport_GetResult_Request;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_GetResult_Request.
typedef struct hospital_interfaces__action__GenerateReport_GetResult_Request__Sequence
{
  hospital_interfaces__action__GenerateReport_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "hospital_interfaces/action/detail/generate_report__struct.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_GetResult_Response
{
  int8_t status;
  hospital_interfaces__action__GenerateReport_Result result;
} hospital_interfaces__action__GenerateReport_GetResult_Response;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_GetResult_Response.
typedef struct hospital_interfaces__action__GenerateReport_GetResult_Response__Sequence
{
  hospital_interfaces__action__GenerateReport_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "hospital_interfaces/action/detail/generate_report__struct.h"

/// Struct defined in action/GenerateReport in the package hospital_interfaces.
typedef struct hospital_interfaces__action__GenerateReport_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  hospital_interfaces__action__GenerateReport_Feedback feedback;
} hospital_interfaces__action__GenerateReport_FeedbackMessage;

// Struct for a sequence of hospital_interfaces__action__GenerateReport_FeedbackMessage.
typedef struct hospital_interfaces__action__GenerateReport_FeedbackMessage__Sequence
{
  hospital_interfaces__action__GenerateReport_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__action__GenerateReport_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__STRUCT_H_
