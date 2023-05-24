"""
This playbook integrates ITSI, SOAR, and your organization&#39;s orchestration framework (such as Puppet, Ansible, or SSM).\n\nIt is designed to serve as a starting point for designing automated troubleshooting workflows.\n\nPlease see the README in the GitHub repo for more details.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'get_episode_info' block
    get_episode_info(container=container)

    return

@phantom.playbook_block()
def get_episode_info(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("get_episode_info() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Retrieve the latest episode metadata from ITSI.
    # 
    # We add a 1-minute delay before we start, so that ITSI has time to fully process 
    # the episode.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.itsi_group_id","artifact:*.id"])

    parameters = []

    # build parameters list for 'get_episode_info' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "itsi_group_id": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    # calculate start time using delay of 1 minutes
    start_time = datetime.now() + timedelta(minutes=1)
    phantom.act("get episode", parameters=parameters, name="get_episode_info", start_time=start_time, assets=["my-itsi-server"], callback=check_if_episode_is_already_assigned)

    return


@phantom.playbook_block()
def check_if_episode_is_already_assigned(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("check_if_episode_is_already_assigned() called")

    ################################################################################
    # Is the episode already assigned to a human?
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["get_episode_info:action_result.data.*.owner", "==", "unassigned"]
        ],
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        assign_episode_to_bot(action=action, success=success, container=container, results=results, handle=handle)
        return

    return


@phantom.playbook_block()
def assign_episode_to_bot(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("assign_episode_to_bot() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Assign the ITSI episode to the SOAR Bot so that engineers don't pick it up by 
    # mistake.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.itsi_group_id","artifact:*.id"])

    parameters = []

    # build parameters list for 'assign_episode_to_bot' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "itsi_group_id": container_artifact_item[0],
                "owner": "soar-bot",
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("update episode", parameters=parameters, name="assign_episode_to_bot", assets=["my-itsi-server"], callback=trigger_disk_cleanup)

    return


@phantom.playbook_block()
def trigger_disk_cleanup(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("trigger_disk_cleanup() called")

    ################################################################################
    # Reach out to your orchestration layer (Puppet, Ansible, SSM, etc.) and trigger 
    # a predefined "disk cleanup" task.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceHostName"])

    container_artifact_cef_item_0 = [item[0] for item in container_artifact_data]

    trigger_disk_cleanup__cleanup_success = None
    trigger_disk_cleanup__cleanup_output = None

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...
    # You can find the hostname of the alerting server in the "target_hostname" variable.
    target_hostname = container_artifact_cef_item_0[0]
    
    # You should make a REST API call to your orchestration framework (Puppet, Ansible, SSM, etc.) to trigger disk cleanup.
    # This is left as an exercise for the reader.
    
    # !!! TODO: add your code here.
    
    # You should populate the output variables with the result of your orchestration command.
    trigger_disk_cleanup__cleanup_success = False
    trigger_disk_cleanup__cleanup_output = "Not yet implemented."
    
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_run_data(key="trigger_disk_cleanup:cleanup_success", value=json.dumps(trigger_disk_cleanup__cleanup_success))
    phantom.save_run_data(key="trigger_disk_cleanup:cleanup_output", value=json.dumps(trigger_disk_cleanup__cleanup_output))

    check_cleanup_result(container=container)

    return


@phantom.playbook_block()
def check_cleanup_result(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("check_cleanup_result() called")

    ################################################################################
    # Was the cleanup successful?
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["trigger_disk_cleanup:custom_function:cleanup_success", "==", True]
        ],
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        comment_success(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    comment_failure(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def comment_success(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("comment_success() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    comment_formatted_string = phantom.format(
        container=container,
        template="""Splunk SOAR has successfully cleaned up the disk.\n\nAutomation output:\n{0}\n""",
        parameters=[
            "trigger_disk_cleanup:custom_function:cleanup_output"
        ])

    ################################################################################
    # Leave a comment on the episode, indicating that we fixed it with automation.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.itsi_group_id","artifact:*.id"])
    trigger_disk_cleanup__cleanup_output = json.loads(_ if (_ := phantom.get_run_data(key="trigger_disk_cleanup:cleanup_output")) != "" else "null")  # pylint: disable=used-before-assignment

    parameters = []

    # build parameters list for 'comment_success' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None and comment_formatted_string is not None:
            parameters.append({
                "itsi_group_id": container_artifact_item[0],
                "comment": comment_formatted_string,
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add episode comment", parameters=parameters, name="comment_success", assets=["my-itsi-server"], callback=close_episode)

    return


@phantom.playbook_block()
def close_episode(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("close_episode() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Close the episode, so that it can be cleared from the ITSI queue.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.itsi_group_id","artifact:*.id"])

    parameters = []

    # build parameters list for 'close_episode' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "itsi_group_id": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("close episode", parameters=parameters, name="close_episode", assets=["my-itsi-server"])

    return


@phantom.playbook_block()
def comment_failure(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("comment_failure() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    comment_formatted_string = phantom.format(
        container=container,
        template="""Splunk SOAR couldn't automatically clean up the disk.\n\nAutomation output:\n{0}""",
        parameters=[
            "trigger_disk_cleanup:custom_function:cleanup_output"
        ])

    ################################################################################
    # Leave a comment on the episode, indicating that we couldn't fix it with automation.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.itsi_group_id","artifact:*.id"])
    trigger_disk_cleanup__cleanup_output = json.loads(_ if (_ := phantom.get_run_data(key="trigger_disk_cleanup:cleanup_output")) != "" else "null")  # pylint: disable=used-before-assignment

    parameters = []

    # build parameters list for 'comment_failure' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None and comment_formatted_string is not None:
            parameters.append({
                "itsi_group_id": container_artifact_item[0],
                "comment": comment_formatted_string,
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add episode comment", parameters=parameters, name="comment_failure", assets=["my-itsi-server"], callback=unassign_episode)

    return


@phantom.playbook_block()
def unassign_episode(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("unassign_episode() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Change the episode back to Unassigned, so that an engineer can work it manually.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.itsi_group_id","artifact:*.id"])

    parameters = []

    # build parameters list for 'unassign_episode' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "itsi_group_id": container_artifact_item[0],
                "owner": "unassigned",
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("update episode", parameters=parameters, name="unassign_episode", assets=["my-itsi-server"])

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    return