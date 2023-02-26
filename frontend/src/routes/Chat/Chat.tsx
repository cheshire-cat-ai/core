import React, { type FC } from 'react'
import { Link } from 'react-router-dom'

/**
 * Chat page component
 */
const Chat: FC = () => {
  return (
    <div>
      <h1>Chat page</h1>
      <Link to="/">Home</Link>
    </div>
  )
}

export default React.memo(Chat)
