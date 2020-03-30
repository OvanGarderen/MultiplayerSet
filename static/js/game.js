var socket = io.connect('http://' + document.domain + ':' + location.port);

var marked_cards = [];
var room_state = null;

// websocket interaction
socket.on('connect', function() {
    console.log('Websocket connected!');
    
    var username = Cookies.get('username');
    var pwhash = Cookies.get('pwhash');
    socket.emit('join', {'username' : username, 'pwhash' : pwhash, 'room' : 'testgame'});
});

socket.on('game_update', function(data) {
    room_state = data;
    update_cards(room_state['board']);
    update_player_info(room_state['players'])
});

socket.on('message', function(message) {
    $("#infobox").prepend(message + "</br>");
});

socket.on('game_over', function(data) {
    update_cards(data['board']);

    $('playarea').addClass('game-over');
});


// game logic
function update_cards(cards) {
    var width = cards.length/3;

    // lay cards on table
    // todo: visual queue that only updates new cards
    var table = "";
    for (i = 0; i < 3; i++) {
	table += '<tr>';
	for (j = 0; j < width; j++) table += '<td><div class="card"></div></td>';
	table += '</tr>';
    }
    $("#cards").html(table);
    
    $("#cards").find('div').each(function (n, el){
	// on click select the card
	$(el).click(function() {
	    // update visually
	    if ($(el).hasClass("marked")) 
		$(el).removeClass("marked");
	    else
		$(el).addClass("marked");

	    // update inner logic
	    toggleCard(n);
	});

	let c = cards[n];
	// change to the right image
	$(el).addClass('card-' +
		       (c['number']==1 ? 'single' : (c['number']==2 ? 'double' : 'triple')) + '-' +
		       (c['shape']=='FLEXYBOY' ? 'squiggle' : (c['shape']=='OVAL' ? 'oval' : 'diamond')) + '-' +				(c['shading']=='SHADED' ? 'dashed' : (c['shading']=='FULL' ? 'full' : 'empty'))
		       + '-' + c['colour']);

    });
}

function update_player_info(players) {
    html = "";

    // todo: move into template on page
    for (var i=0; i < players.length; i++) 
	html += "<div class='playerinfo internal-box'><table><tr><td>" + decodeURIComponent(players[i]['username']) +  "<td></tr><tr><td>Sets: " + players[i]['sets'] + "<td></tr></table></div>";

    $("#players").html(html);	
}

function toggleCard(n) {
    // check if card was already selected
    if (marked_cards.indexOf(n) < 0) {
	marked_cards.push(n);

	// user has selected a set, ask the server if its ok
	if (marked_cards.length >= 3) {
	    socket.emit('set_select', {
		'room' : room_state['id'], 
		'username' : 'testuser', 
		'pwhash' : 'test',
		'selection' : marked_cards
	    });

	    marked_cards = [];
	}	    
    } else {
	// remove card from the list
	marked_cards = marked_cards.filter(function(value,index,arr){return value != n});
    }
}

// start the game
function Draw() {
    $('playarea').removeClass('game-over');

    socket.emit('testdraw');
}
