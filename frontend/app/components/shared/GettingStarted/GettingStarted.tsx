import React from 'react';
import StepList, { Step } from './StepList';
import Modal from 'App/components/Modal/Modal';

export interface Props {
  list: Step[];
}

function GettingStarted(props: Props) {
  const { list } = props;
  const pendingSteps = list.filter((step) => step.status === 'pending');
  const completedSteps = list.filter(
    (step) => step.status === 'completed' || step.status === 'ignored'
  );

  return (
    <>
      <Modal.Header title="Setup Openreplay">
        <div className="px-4 pt-4">
          <div className="text-lg">Setup Openreplay</div>
          <p>Find all the ways in which OpenReplay can benefit you and your product.</p>
        </div>
      </Modal.Header>

      <Modal.Content className="p-4 pb-20">
        <StepList title="Pending" steps={pendingSteps} status="pending" />
        <StepList title="Completed" steps={completedSteps} status="completed" />
      </Modal.Content>
    </>
  );
}

export default GettingStarted;
