// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hospital_interfaces:srv/AnalyzeActivity.idl
// generated code does not contain a copyright notice
#include "hospital_interfaces/srv/detail/analyze_activity__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `image_path`
// Member `zone_name`
// Member `time`
// Member `expected_activities`
// Member `zone_type`
#include "rosidl_runtime_c/string_functions.h"

bool
hospital_interfaces__srv__AnalyzeActivity_Request__init(hospital_interfaces__srv__AnalyzeActivity_Request * msg)
{
  if (!msg) {
    return false;
  }
  // image_path
  if (!rosidl_runtime_c__String__init(&msg->image_path)) {
    hospital_interfaces__srv__AnalyzeActivity_Request__fini(msg);
    return false;
  }
  // zone_name
  if (!rosidl_runtime_c__String__init(&msg->zone_name)) {
    hospital_interfaces__srv__AnalyzeActivity_Request__fini(msg);
    return false;
  }
  // time
  if (!rosidl_runtime_c__String__init(&msg->time)) {
    hospital_interfaces__srv__AnalyzeActivity_Request__fini(msg);
    return false;
  }
  // expected_activities
  if (!rosidl_runtime_c__String__init(&msg->expected_activities)) {
    hospital_interfaces__srv__AnalyzeActivity_Request__fini(msg);
    return false;
  }
  // zone_type
  if (!rosidl_runtime_c__String__init(&msg->zone_type)) {
    hospital_interfaces__srv__AnalyzeActivity_Request__fini(msg);
    return false;
  }
  return true;
}

void
hospital_interfaces__srv__AnalyzeActivity_Request__fini(hospital_interfaces__srv__AnalyzeActivity_Request * msg)
{
  if (!msg) {
    return;
  }
  // image_path
  rosidl_runtime_c__String__fini(&msg->image_path);
  // zone_name
  rosidl_runtime_c__String__fini(&msg->zone_name);
  // time
  rosidl_runtime_c__String__fini(&msg->time);
  // expected_activities
  rosidl_runtime_c__String__fini(&msg->expected_activities);
  // zone_type
  rosidl_runtime_c__String__fini(&msg->zone_type);
}

bool
hospital_interfaces__srv__AnalyzeActivity_Request__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Request * lhs, const hospital_interfaces__srv__AnalyzeActivity_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // image_path
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->image_path), &(rhs->image_path)))
  {
    return false;
  }
  // zone_name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->zone_name), &(rhs->zone_name)))
  {
    return false;
  }
  // time
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->time), &(rhs->time)))
  {
    return false;
  }
  // expected_activities
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->expected_activities), &(rhs->expected_activities)))
  {
    return false;
  }
  // zone_type
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->zone_type), &(rhs->zone_type)))
  {
    return false;
  }
  return true;
}

bool
hospital_interfaces__srv__AnalyzeActivity_Request__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Request * input,
  hospital_interfaces__srv__AnalyzeActivity_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // image_path
  if (!rosidl_runtime_c__String__copy(
      &(input->image_path), &(output->image_path)))
  {
    return false;
  }
  // zone_name
  if (!rosidl_runtime_c__String__copy(
      &(input->zone_name), &(output->zone_name)))
  {
    return false;
  }
  // time
  if (!rosidl_runtime_c__String__copy(
      &(input->time), &(output->time)))
  {
    return false;
  }
  // expected_activities
  if (!rosidl_runtime_c__String__copy(
      &(input->expected_activities), &(output->expected_activities)))
  {
    return false;
  }
  // zone_type
  if (!rosidl_runtime_c__String__copy(
      &(input->zone_type), &(output->zone_type)))
  {
    return false;
  }
  return true;
}

hospital_interfaces__srv__AnalyzeActivity_Request *
hospital_interfaces__srv__AnalyzeActivity_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hospital_interfaces__srv__AnalyzeActivity_Request * msg = (hospital_interfaces__srv__AnalyzeActivity_Request *)allocator.allocate(sizeof(hospital_interfaces__srv__AnalyzeActivity_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hospital_interfaces__srv__AnalyzeActivity_Request));
  bool success = hospital_interfaces__srv__AnalyzeActivity_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hospital_interfaces__srv__AnalyzeActivity_Request__destroy(hospital_interfaces__srv__AnalyzeActivity_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hospital_interfaces__srv__AnalyzeActivity_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__init(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hospital_interfaces__srv__AnalyzeActivity_Request * data = NULL;

  if (size) {
    data = (hospital_interfaces__srv__AnalyzeActivity_Request *)allocator.zero_allocate(size, sizeof(hospital_interfaces__srv__AnalyzeActivity_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hospital_interfaces__srv__AnalyzeActivity_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hospital_interfaces__srv__AnalyzeActivity_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__fini(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      hospital_interfaces__srv__AnalyzeActivity_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

hospital_interfaces__srv__AnalyzeActivity_Request__Sequence *
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array = (hospital_interfaces__srv__AnalyzeActivity_Request__Sequence *)allocator.allocate(sizeof(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__destroy(hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * lhs, const hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hospital_interfaces__srv__AnalyzeActivity_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hospital_interfaces__srv__AnalyzeActivity_Request__Sequence__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * input,
  hospital_interfaces__srv__AnalyzeActivity_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hospital_interfaces__srv__AnalyzeActivity_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hospital_interfaces__srv__AnalyzeActivity_Request * data =
      (hospital_interfaces__srv__AnalyzeActivity_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hospital_interfaces__srv__AnalyzeActivity_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hospital_interfaces__srv__AnalyzeActivity_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hospital_interfaces__srv__AnalyzeActivity_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `report`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
hospital_interfaces__srv__AnalyzeActivity_Response__init(hospital_interfaces__srv__AnalyzeActivity_Response * msg)
{
  if (!msg) {
    return false;
  }
  // report
  if (!rosidl_runtime_c__String__init(&msg->report)) {
    hospital_interfaces__srv__AnalyzeActivity_Response__fini(msg);
    return false;
  }
  return true;
}

void
hospital_interfaces__srv__AnalyzeActivity_Response__fini(hospital_interfaces__srv__AnalyzeActivity_Response * msg)
{
  if (!msg) {
    return;
  }
  // report
  rosidl_runtime_c__String__fini(&msg->report);
}

bool
hospital_interfaces__srv__AnalyzeActivity_Response__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Response * lhs, const hospital_interfaces__srv__AnalyzeActivity_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // report
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->report), &(rhs->report)))
  {
    return false;
  }
  return true;
}

bool
hospital_interfaces__srv__AnalyzeActivity_Response__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Response * input,
  hospital_interfaces__srv__AnalyzeActivity_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // report
  if (!rosidl_runtime_c__String__copy(
      &(input->report), &(output->report)))
  {
    return false;
  }
  return true;
}

hospital_interfaces__srv__AnalyzeActivity_Response *
hospital_interfaces__srv__AnalyzeActivity_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hospital_interfaces__srv__AnalyzeActivity_Response * msg = (hospital_interfaces__srv__AnalyzeActivity_Response *)allocator.allocate(sizeof(hospital_interfaces__srv__AnalyzeActivity_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hospital_interfaces__srv__AnalyzeActivity_Response));
  bool success = hospital_interfaces__srv__AnalyzeActivity_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hospital_interfaces__srv__AnalyzeActivity_Response__destroy(hospital_interfaces__srv__AnalyzeActivity_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hospital_interfaces__srv__AnalyzeActivity_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__init(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hospital_interfaces__srv__AnalyzeActivity_Response * data = NULL;

  if (size) {
    data = (hospital_interfaces__srv__AnalyzeActivity_Response *)allocator.zero_allocate(size, sizeof(hospital_interfaces__srv__AnalyzeActivity_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hospital_interfaces__srv__AnalyzeActivity_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hospital_interfaces__srv__AnalyzeActivity_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__fini(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      hospital_interfaces__srv__AnalyzeActivity_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

hospital_interfaces__srv__AnalyzeActivity_Response__Sequence *
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array = (hospital_interfaces__srv__AnalyzeActivity_Response__Sequence *)allocator.allocate(sizeof(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__destroy(hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__are_equal(const hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * lhs, const hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hospital_interfaces__srv__AnalyzeActivity_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hospital_interfaces__srv__AnalyzeActivity_Response__Sequence__copy(
  const hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * input,
  hospital_interfaces__srv__AnalyzeActivity_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hospital_interfaces__srv__AnalyzeActivity_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hospital_interfaces__srv__AnalyzeActivity_Response * data =
      (hospital_interfaces__srv__AnalyzeActivity_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hospital_interfaces__srv__AnalyzeActivity_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hospital_interfaces__srv__AnalyzeActivity_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hospital_interfaces__srv__AnalyzeActivity_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
