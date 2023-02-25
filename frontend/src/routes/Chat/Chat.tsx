import React, { type FC } from 'react'

/**
 * Chat page component
 */
const Chat: FC = () => {
  console.log('Rendering chat...')
  return (
    <h1>Chat page</h1>
  )
}

export default React.memo(Chat)
