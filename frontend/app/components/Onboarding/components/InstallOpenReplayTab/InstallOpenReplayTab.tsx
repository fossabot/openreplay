import React from 'react';
import OnboardingTabs from '../OnboardingTabs';
import ProjectFormButton from '../ProjectFormButton';
import { Button, Icon } from 'UI';
import withOnboarding from '../withOnboarding';
import { WithOnboardingProps } from '../withOnboarding';
import { OB_TABS } from 'App/routes';

interface Props extends WithOnboardingProps {}

function InstallOpenReplayTab(props: Props) {
  const { site } = props;
  return (
    <>
      <h1 className="flex items-center px-4 py-3 border-b justify-between">
        <div className="flex items-center text-2xl">
          <span>👋</span>
          <div className="ml-3 flex items-end">
            <span>Hey there! Setup</span>
            <ProjectFormButton />
          </div>
        </div>
        <a className="flex items-center link" href="https://docs.openreplay.com/en/installation/javascript-sdk/" target="_blank">
          <Icon name="book" color="blue" className="mr-2" size={16} />
          <span>Setup Guide</span>
        </a>
      </h1>
      <div className="p-4">
        <div className="mb-6 text-lg font-medium">
          Setup OpenReplay through NPM package <span className="text-sm">(recommended)</span> or
          script.
        </div>
        <OnboardingTabs site={site} />
      </div>
      <div className="border-t px-4 py-3 flex justify-end">
        <Button
          variant="primary"
          className=""
          onClick={() => (props.navTo ? props.navTo(OB_TABS.IDENTIFY_USERS) : null)}
        >
          Identify Users
          <Icon name="arrow-right-short" color="white" size={20} />
        </Button>
      </div>
    </>
  );
}

export default withOnboarding(InstallOpenReplayTab);
