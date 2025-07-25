import { ActionButton } from '@lib/components/ActionButton';
import { ApiEndpoints } from '@lib/enums/ApiEndpoints';
import { ModelType } from '@lib/enums/ModelType';
import { apiUrl } from '@lib/functions/Api';
import { t } from '@lingui/core/macro';
import { hideNotification, showNotification } from '@mantine/notifications';
import { IconBell } from '@tabler/icons-react';
import type { JSX } from 'react';
import { useApi } from '../../contexts/ApiContext';

export default function StarredToggleButton({
  instance,
  model,
  successFunction
}: Readonly<{
  instance: any;
  model: ModelType.part | ModelType.partcategory;
  successFunction: () => void;
}>): JSX.Element {
  const api = useApi();

  function change(starred: boolean, partPk: number) {
    api
      .patch(
        apiUrl(
          model == ModelType.part
            ? ApiEndpoints.part_list
            : ApiEndpoints.category_list,
          partPk
        ),
        { starred: !starred }
      )
      .then(() => {
        hideNotification('subscription-update');
        showNotification({
          title: t`Subscription Updated`,
          id: 'subscription-update',
          message: `Subscription ${starred ? 'removed' : 'added'}`,
          autoClose: 5000,
          color: 'blue'
        });
        successFunction();
      })
      .catch((error) => {
        showNotification({
          title: 'Error',
          message: error.message,
          autoClose: 5000,
          color: 'red'
        });
      });
  }

  return (
    <ActionButton
      icon={<IconBell />}
      color={instance.starred ? 'green' : 'blue'}
      size='lg'
      variant={instance.starred ? 'filled' : 'outline'}
      tooltip={
        instance.starred
          ? t`Unsubscribe from notifications`
          : t`Subscribe to notifications`
      }
      onClick={() => change(instance.starred, instance.pk)}
      tooltipAlignment='bottom'
    />
  );
}
