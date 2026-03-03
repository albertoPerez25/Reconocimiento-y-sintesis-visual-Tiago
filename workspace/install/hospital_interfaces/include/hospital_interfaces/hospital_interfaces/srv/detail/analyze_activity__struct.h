// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hospital_interfaces:srv/AnalyzeActivity.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__STRUCT_H_
#define HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'image_path'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/AnalyzeActivity in the package hospital_interfaces.
typedef struct hospital_interfaces__srv__AnalyzeActivity_Request
{
  /// Request: ruta absoluta de la imagen a analizar
  rosidl_runtime_c__String image_path;
} hospital_interfaces__srv__AnalyzeActivity_Request;

// Struct for a sequence of hospital_interfaces__srv__AnalyzeActivity_Request.
typedef struct hospital_interfaces__srv__AnalyzeActivity_Request__Sequence
{
  hospital_interfaces__srv__AnalyzeActivity_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__srv__AnalyzeActivity_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'report'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/AnalyzeActivity in the package hospital_interfaces.
typedef struct hospital_interfaces__srv__AnalyzeActivity_Response
{
  /// Response: texto con la descripción de las personas
  rosidl_runtime_c__String report;
} hospital_interfaces__srv__AnalyzeActivity_Response;

// Struct for a sequence of hospital_interfaces__srv__AnalyzeActivity_Response.
typedef struct hospital_interfaces__srv__AnalyzeActivity_Response__Sequence
{
  hospital_interfaces__srv__AnalyzeActivity_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hospital_interfaces__srv__AnalyzeActivity_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__STRUCT_H_
