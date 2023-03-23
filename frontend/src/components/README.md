## Components

The components that are specified within this particular directory are Stateless Components, meaning that they do not
have knowledge of the state of the application and are exclusively focused on the user interface. These components
should not be linked to the state manager, and any state that is required should be injected via props unless it is an
absolute necessity.

Below is a code snippet that can be used as a reference for these components:

```tsx
// ComponentName.tsx
import React, { FC } from 'react'
import { CommonProps } from '@models/commons'

import styles from './ComponentName.module.scss'

/**
 * ComponentName documentation goes here
 */
const ComponentName: FC<ComponentNameProps> = ({ className, ...rest }) => {
  const classList = clsx(styles.componentName, props.className)

  return (
    <div className={classList}>
      <h1>ComponentName</h1>
    </div>
  )
}

export interface ComponentNameProps extends CommonProps {
  // Props that are required
  requiredProp: string;
  // Props that are optional
  optionalProp?: string;
}

export default ComponentName
```

```scss
// ComponentName.module.scss
.componentName {
  /* Styles go here */
  /* You can use global variables from src/theme/_variables.scss directly without any import */
  /* You can use global mixins from src/theme/_mixins.scss directly without any import */
}
```

```ts
// index.ts
export { default } from './ComponentName'
export type { ComponentNameProps } from './ComponentName'
```
