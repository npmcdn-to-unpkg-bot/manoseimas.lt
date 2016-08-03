import React, { PropTypes } from 'react'
import { StatusBar, FacebookShare } from '../../components'
import Tabs from './Tabs'
import styles from '../../styles/views/results.css'

export const ResultsLayout = ({ children }) =>
    <div>
        <header>
            <img src='/static/img/logo-black.png' className='logo' />
            <StatusBar current={12} max={12} />
        </header>
        <div className={styles.content}>
            <h2 className='title'>Rezultatai</h2>
            <Tabs />
            {children}
        </div>
        <div className={styles.side}>
            <FacebookShare responseHandler={(response) => (console.log(response))} />
        </div>
    </div>

ResultsLayout.propTyoes = {
    children: PropTypes.element.isRequired
}

export default ResultsLayout