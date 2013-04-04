#_require utils.coffee
#_require ui.coffee

window.MSWidget = {
    content: undefined,
    profile: undefined,

    load_voting: (voting_id) ->
        $("#MSWidget").innerHTML = render "loading-frame"
        fetch_voting voting_id, (data) ->
            if data.error
                MSWidget.content = undefined
                $("#MSWidget").innerHTML = render "error-pane", { message: "Problem loading voting `#{voting_id}`: #{data.error}" }
            else 
                MSWidget.content = data
                $("#MSWidget").innerHTML = render "widget-frame", MSWidget.content
                ui_refresh() 
                MSWidget.show_fractions()

    load_profile: (profile_id, callback) ->
        fetch_profile profile_id, (profile) ->
            MSWidget.profile = profile
            callback profile if callback?

    vote: (position) ->
        position *= 2 if $("#important").checked
        update_position MSWidget.content.voting._id, position
        
        MSWidget.show_thanks()

    connect: (service) ->
        # Different tweaks for different services
        switch service
            when "google"
                [w,h] = [450, 500]
                url = "/widget/auth/google/popup"
            when "facebook"
                [w,h] = [100,100]
                url = "/accounts/login/facebook"
            when "openid"
                [w,h] = [650, 300]
                url = "/accounts/login/"

        x = screen.width/2 - w/2
        y = screen.height/2 - h/2
        window.open url+"?next=/widget/auth/finish", "", "width=#{w},height=#{h},status=1,location=1,resizable=yes,left=#{x},top=#{y}"
    
    connected: (profile_id) ->
        MSWidget.load_profile profile_id, (profile) ->
            MSWidget.show_thanks true



    show_fractions: () -> MSWidget.show_panel 'fractions'
    show_mps: (subpanel) -> 
        MSWidget.show_panel 'mps'
        if subpanel?
            $("#MSWidget-mps-#{subpanel}").offsetParent.scrollTop = $("#MSWidget-mps-#{subpanel}").offsetTop
            for sp in ['aye','no','abstain']
                if subpanel is sp
                    $("#MSWidget-mps-#{sp}_button").style.backgroundColor = '#ccc'
                else 
                    $("#MSWidget-mps-#{sp}_button").style.backgroundColor = '#fff'


    show_panel: (panel) ->
        for p in ['fractions', 'mps']
            if panel is p
                show $("#MSWidget-#{p}")
                $("#MSWidget-#{p}_button").style.backgroundColor = '#ccc'
            else 
                hide $("#MSWidget-#{p}")
                $("#MSWidget-#{p}_button").style.backgroundColor = '#fff'

    hide_overlays: () -> 
        hide o for o in $(".overlay")

    show_thanks: (rerender=true) ->
        MSWidget.hide_overlays()
        if rerender? or $("#MSWidget-thanks").innerHTML is ""
            $("#MSWidget-thanks").innerHTML = render "thanks-pane", { profile: MSWidget.profile }

        show $("#MSWidget-thanks")

    show_overlay: (name) ->
        MSWidget.hide_overlays();
        show $("#MSWidget-#{name}")
    
}
