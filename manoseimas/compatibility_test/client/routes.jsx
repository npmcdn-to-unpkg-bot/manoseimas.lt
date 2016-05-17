import React from 'react'
import { IndexRoute, Route } from 'react-router'
import Layout from './app/layout'
import { StartTest, Question } from './app/TestView'

export default (store) => {
    /**
     * Please keep routes in alphabetical order
     */

    let compo = <div>Hello J</div>
    return (
        <Route path="/" component={Layout}>
            <IndexRoute component={StartTest}/>

            <Route path="/q" component={Question}/>
        </Route>
    )
}