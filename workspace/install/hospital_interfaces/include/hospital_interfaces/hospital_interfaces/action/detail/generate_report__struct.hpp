// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hospital_interfaces:action/GenerateReport.idl
// generated code does not contain a copyright notice

#ifndef HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__STRUCT_HPP_
#define HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_Goal __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_Goal __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_Goal_
{
  using Type = GenerateReport_Goal_<ContainerAllocator>;

  explicit GenerateReport_Goal_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->folder_path = "";
    }
  }

  explicit GenerateReport_Goal_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : folder_path(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->folder_path = "";
    }
  }

  // field types and members
  using _folder_path_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _folder_path_type folder_path;

  // setters for named parameter idiom
  Type & set__folder_path(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->folder_path = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_Goal
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_Goal
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_Goal_ & other) const
  {
    if (this->folder_path != other.folder_path) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_Goal_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_Goal_

// alias to use template instance with default allocator
using GenerateReport_Goal =
  hospital_interfaces::action::GenerateReport_Goal_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_Result __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_Result __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_Result_
{
  using Type = GenerateReport_Result_<ContainerAllocator>;

  explicit GenerateReport_Result_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->final_report = "";
    }
  }

  explicit GenerateReport_Result_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : final_report(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->final_report = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _final_report_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _final_report_type final_report;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__final_report(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->final_report = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_Result
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_Result
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_Result_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->final_report != other.final_report) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_Result_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_Result_

// alias to use template instance with default allocator
using GenerateReport_Result =
  hospital_interfaces::action::GenerateReport_Result_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces


#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_Feedback __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_Feedback __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_Feedback_
{
  using Type = GenerateReport_Feedback_<ContainerAllocator>;

  explicit GenerateReport_Feedback_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->current_zone = "";
      this->percentage_complete = 0.0f;
    }
  }

  explicit GenerateReport_Feedback_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : current_zone(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->current_zone = "";
      this->percentage_complete = 0.0f;
    }
  }

  // field types and members
  using _current_zone_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _current_zone_type current_zone;
  using _percentage_complete_type =
    float;
  _percentage_complete_type percentage_complete;

  // setters for named parameter idiom
  Type & set__current_zone(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->current_zone = _arg;
    return *this;
  }
  Type & set__percentage_complete(
    const float & _arg)
  {
    this->percentage_complete = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_Feedback
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_Feedback
    std::shared_ptr<hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_Feedback_ & other) const
  {
    if (this->current_zone != other.current_zone) {
      return false;
    }
    if (this->percentage_complete != other.percentage_complete) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_Feedback_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_Feedback_

// alias to use template instance with default allocator
using GenerateReport_Feedback =
  hospital_interfaces::action::GenerateReport_Feedback_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces


// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'goal'
#include "hospital_interfaces/action/detail/generate_report__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Request __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Request __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_SendGoal_Request_
{
  using Type = GenerateReport_SendGoal_Request_<ContainerAllocator>;

  explicit GenerateReport_SendGoal_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init),
    goal(_init)
  {
    (void)_init;
  }

  explicit GenerateReport_SendGoal_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init),
    goal(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;
  using _goal_type =
    hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator>;
  _goal_type goal;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }
  Type & set__goal(
    const hospital_interfaces::action::GenerateReport_Goal_<ContainerAllocator> & _arg)
  {
    this->goal = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Request
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Request
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_SendGoal_Request_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    if (this->goal != other.goal) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_SendGoal_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_SendGoal_Request_

// alias to use template instance with default allocator
using GenerateReport_SendGoal_Request =
  hospital_interfaces::action::GenerateReport_SendGoal_Request_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces


// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Response __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Response __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_SendGoal_Response_
{
  using Type = GenerateReport_SendGoal_Response_<ContainerAllocator>;

  explicit GenerateReport_SendGoal_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  explicit GenerateReport_SendGoal_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  // field types and members
  using _accepted_type =
    bool;
  _accepted_type accepted;
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;

  // setters for named parameter idiom
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Response
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_SendGoal_Response
    std::shared_ptr<hospital_interfaces::action::GenerateReport_SendGoal_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_SendGoal_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_SendGoal_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_SendGoal_Response_

// alias to use template instance with default allocator
using GenerateReport_SendGoal_Response =
  hospital_interfaces::action::GenerateReport_SendGoal_Response_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces

namespace hospital_interfaces
{

namespace action
{

struct GenerateReport_SendGoal
{
  using Request = hospital_interfaces::action::GenerateReport_SendGoal_Request;
  using Response = hospital_interfaces::action::GenerateReport_SendGoal_Response;
};

}  // namespace action

}  // namespace hospital_interfaces


// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Request __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Request __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_GetResult_Request_
{
  using Type = GenerateReport_GetResult_Request_<ContainerAllocator>;

  explicit GenerateReport_GetResult_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init)
  {
    (void)_init;
  }

  explicit GenerateReport_GetResult_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Request
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Request
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_GetResult_Request_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_GetResult_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_GetResult_Request_

// alias to use template instance with default allocator
using GenerateReport_GetResult_Request =
  hospital_interfaces::action::GenerateReport_GetResult_Request_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces


// Include directives for member types
// Member 'result'
// already included above
// #include "hospital_interfaces/action/detail/generate_report__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Response __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Response __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_GetResult_Response_
{
  using Type = GenerateReport_GetResult_Response_<ContainerAllocator>;

  explicit GenerateReport_GetResult_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  explicit GenerateReport_GetResult_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  // field types and members
  using _status_type =
    int8_t;
  _status_type status;
  using _result_type =
    hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator>;
  _result_type result;

  // setters for named parameter idiom
  Type & set__status(
    const int8_t & _arg)
  {
    this->status = _arg;
    return *this;
  }
  Type & set__result(
    const hospital_interfaces::action::GenerateReport_Result_<ContainerAllocator> & _arg)
  {
    this->result = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Response
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_GetResult_Response
    std::shared_ptr<hospital_interfaces::action::GenerateReport_GetResult_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_GetResult_Response_ & other) const
  {
    if (this->status != other.status) {
      return false;
    }
    if (this->result != other.result) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_GetResult_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_GetResult_Response_

// alias to use template instance with default allocator
using GenerateReport_GetResult_Response =
  hospital_interfaces::action::GenerateReport_GetResult_Response_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces

namespace hospital_interfaces
{

namespace action
{

struct GenerateReport_GetResult
{
  using Request = hospital_interfaces::action::GenerateReport_GetResult_Request;
  using Response = hospital_interfaces::action::GenerateReport_GetResult_Response;
};

}  // namespace action

}  // namespace hospital_interfaces


// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'feedback'
// already included above
// #include "hospital_interfaces/action/detail/generate_report__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hospital_interfaces__action__GenerateReport_FeedbackMessage __attribute__((deprecated))
#else
# define DEPRECATED__hospital_interfaces__action__GenerateReport_FeedbackMessage __declspec(deprecated)
#endif

namespace hospital_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct GenerateReport_FeedbackMessage_
{
  using Type = GenerateReport_FeedbackMessage_<ContainerAllocator>;

  explicit GenerateReport_FeedbackMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init),
    feedback(_init)
  {
    (void)_init;
  }

  explicit GenerateReport_FeedbackMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init),
    feedback(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;
  using _feedback_type =
    hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator>;
  _feedback_type feedback;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }
  Type & set__feedback(
    const hospital_interfaces::action::GenerateReport_Feedback_<ContainerAllocator> & _arg)
  {
    this->feedback = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_FeedbackMessage
    std::shared_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hospital_interfaces__action__GenerateReport_FeedbackMessage
    std::shared_ptr<hospital_interfaces::action::GenerateReport_FeedbackMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateReport_FeedbackMessage_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    if (this->feedback != other.feedback) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateReport_FeedbackMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateReport_FeedbackMessage_

// alias to use template instance with default allocator
using GenerateReport_FeedbackMessage =
  hospital_interfaces::action::GenerateReport_FeedbackMessage_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace hospital_interfaces

#include "action_msgs/srv/cancel_goal.hpp"
#include "action_msgs/msg/goal_info.hpp"
#include "action_msgs/msg/goal_status_array.hpp"

namespace hospital_interfaces
{

namespace action
{

struct GenerateReport
{
  /// The goal message defined in the action definition.
  using Goal = hospital_interfaces::action::GenerateReport_Goal;
  /// The result message defined in the action definition.
  using Result = hospital_interfaces::action::GenerateReport_Result;
  /// The feedback message defined in the action definition.
  using Feedback = hospital_interfaces::action::GenerateReport_Feedback;

  struct Impl
  {
    /// The send_goal service using a wrapped version of the goal message as a request.
    using SendGoalService = hospital_interfaces::action::GenerateReport_SendGoal;
    /// The get_result service using a wrapped version of the result message as a response.
    using GetResultService = hospital_interfaces::action::GenerateReport_GetResult;
    /// The feedback message with generic fields which wraps the feedback message.
    using FeedbackMessage = hospital_interfaces::action::GenerateReport_FeedbackMessage;

    /// The generic service to cancel a goal.
    using CancelGoalService = action_msgs::srv::CancelGoal;
    /// The generic message for the status of a goal.
    using GoalStatusMessage = action_msgs::msg::GoalStatusArray;
  };
};

typedef struct GenerateReport GenerateReport;

}  // namespace action

}  // namespace hospital_interfaces

#endif  // HOSPITAL_INTERFACES__ACTION__DETAIL__GENERATE_REPORT__STRUCT_HPP_
