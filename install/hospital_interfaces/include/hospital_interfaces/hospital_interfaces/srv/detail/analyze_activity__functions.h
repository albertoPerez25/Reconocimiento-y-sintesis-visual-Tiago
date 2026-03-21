// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from hospital_interfaces:srv/AnalyzeActivity.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__FUNCTIONS_H_
#define HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "hospital_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "hospital_interfaces/srv/detail/analyze_activity__struct.h"

/// Initialize srv/AnalyzeActivity message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * hospital_interfaces__srv__AnalyzeActivity_Request
 * )) before or use
 * hospital_interfaces__srv__AnalyzeActivity_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Request__init(hospital_interfaces__srv__AnalyzeActivity_Request * msg);

/// Finalize srv/AnalyzeActivity message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Request__fini(hospital_interfaces__srv__AnalyzeActivity_Request * msg);

/// Create srv/AnalyzeActivity message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * hospital_interfaces__srv__AnalyzeActivity_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
hospital_interfaces__srv__AnalyzeActivity_Request *
hospital_interfaces__srv__AnalyzeActivity_Request__create();

/// Destroy srv/AnalyzeActivity message.
/**
 * It calls
 * hospital_interfaces__srv__AnalyzeActivity_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Request__destroy(hospital_interfaces__srv__AnalyzeActivity_Request * msg);

/// Check for srv/AnalyzeActivity message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Request__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Request * lhs, const hospital_interfaces__srv__AnalyzeActivity_Request * rhs);

/// Copy a srv/AnalyzeActivity message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Request__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Request * input,
  hospital_interfaces__srv__AnalyzeActivity_Request * output);

/// Initialize array of srv/AnalyzeActivity messages.
/**
 * It allocates the memory for the number of elements and calls
 * hospital_interfaces__srv__AnalyzeActivity_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__init(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array, size_t size);

/// Finalize array of srv/AnalyzeActivity messages.
/**
 * It calls
 * hospital_interfaces__srv__AnalyzeActivity_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__fini(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array);

/// Create array of srv/AnalyzeActivity messages.
/**
 * It allocates the memory for the array and calls
 * hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence *
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__create(size_t size);

/// Destroy array of srv/AnalyzeActivity messages.
/**
 * It calls
 * hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__destroy(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array);

/// Check for srv/AnalyzeActivity message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * lhs, const hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * rhs);

/// Copy an array of srv/AnalyzeActivity messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * input,
  hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * output);

/// Initialize srv/AnalyzeActivity message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * hospital_interfaces__srv__AnalyzeActivity_Response
 * )) before or use
 * hospital_interfaces__srv__AnalyzeActivity_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Response__init(hospital_interfaces__srv__AnalyzeActivity_Response * msg);

/// Finalize srv/AnalyzeActivity message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Response__fini(hospital_interfaces__srv__AnalyzeActivity_Response * msg);

/// Create srv/AnalyzeActivity message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * hospital_interfaces__srv__AnalyzeActivity_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
hospital_interfaces__srv__AnalyzeActivity_Response *
hospital_interfaces__srv__AnalyzeActivity_Response__create();

/// Destroy srv/AnalyzeActivity message.
/**
 * It calls
 * hospital_interfaces__srv__AnalyzeActivity_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Response__destroy(hospital_interfaces__srv__AnalyzeActivity_Response * msg);

/// Check for srv/AnalyzeActivity message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Response__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Response * lhs, const hospital_interfaces__srv__AnalyzeActivity_Response * rhs);

/// Copy a srv/AnalyzeActivity message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Response__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Response * input,
  hospital_interfaces__srv__AnalyzeActivity_Response * output);

/// Initialize array of srv/AnalyzeActivity messages.
/**
 * It allocates the memory for the number of elements and calls
 * hospital_interfaces__srv__AnalyzeActivity_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__init(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array, size_t size);

/// Finalize array of srv/AnalyzeActivity messages.
/**
 * It calls
 * hospital_interfaces__srv__AnalyzeActivity_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__fini(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array);

/// Create array of srv/AnalyzeActivity messages.
/**
 * It allocates the memory for the array and calls
 * hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence *
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__create(size_t size);

/// Destroy array of srv/AnalyzeActivity messages.
/**
 * It calls
 * hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
void
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__destroy(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array);

/// Check for srv/AnalyzeActivity message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * lhs, const hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * rhs);

/// Copy an array of srv/AnalyzeActivity messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_hospital_interfaces
bool
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * input,
  hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // HOSPITAL_INTERFACES__SRV__DETAIL__ANALYZE_ACTIVITY__FUNCTIONS_H_
