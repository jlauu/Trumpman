// app.js - top-level private module for hangman as a single-page application
// Note: This uses ES6 only tested in Chrome!

document.addEventListener("DOMContentLoaded", function(event) {
  "use strict"; 
  let _state = {
    status: null,
    incorrect_guesses: null,
    max_guesses: null,
    guesses_left: null,
    letters_guessed: null,
    word_with_blanks: null,
    won: null,
    lost: null,
    // Non-null when gameover status
    letters_left: null,
    answer: null
  };

  const valid_letters = /^[a-zA-z]$/i;

  const ids = {
    header: 'header',
    content: 'content',
    footer: 'footer',
    hangman: 'hangman',
    btn: 'btn',
    blanks: 'blanks',
    letter: 'letter',
    counter: 'counter',
    message: 'message',
    infobox: 'infobox',
    dirs: 'directions',
    piece: i => 'hangman-'+i
  };

  const api = (() => {
    const getJSON = response => {
      if (response.ok)
        return response.json()
      else
        throw response
    };
    const get = {
        method: 'GET',
        credentials: "same-origin"
    };
    const post = {
        method: 'POST',
        credentials: "same-origin"
    };
    return {
      new_game: () => fetch('/game/new', post).then(getJSON),
      get_game: () => fetch('/game', get).then(getJSON),
      guess: (c) => fetch('/guess/'+c, post).then(getJSON)
    };
  })();

  // Static containers should be rendered in static html
  const containers = {
    header: $('#'+ids.header),
    content: $('#'+ids.content),
    footer: $('#'+ids.footer),
    hangman: $('#'+ids.hangman)
  };

  // Dynamic containers created and destroyed depending on game state
  const factory = {
    title: () => $(`
      <h1 class="ui huge header">
        <span style="color: red">Trump</span>
        <span style="color: blue">man</span>
      </h1>`),
    btn: (text) => $(`
      <button id="${ids.btn}" class="ui button">
        ${text}
      </button>
    `),
    counter: (g) => $(`
      <h1 id="${ids.counter}">${g} guesses remaining</h1>
    `),
    blanks: () => $(`
      <div id="${ids.blanks}"></div>
    `),
    letter: (c) => $(`
      <div class="${ids.letter}">
        <div class="ui raised segment">
          <h1>${c.toUpperCase()}</h1>
        </div>
      </div>
    `),
    message: (text) => $(`
      <h2 id="${ids.message}">${text}</h2>
    `),
    infobox: () => $(`
      <div id="${ids.infobox}" class="ui raised segment"></div>
    `),
    directions: () => $(`
      <div id="${ids.dirs}">
        <h4>Can you guess what word Trump is thinking?</h4>
        <h4>Press a letter on the keyboard to make a guess</h4>
        <h4>Hit 'Enter' to start</h4>
      </div>
    `),
  };

  // Event handlers
  
  const enterToPress = btn => {
    const callback = e => {
      if (e.keyCode && e.keyCode === 13) {
        btn.click();
      }
    };
    return {
      callback,
      remove: () => $(document).off('keypress', callback),
      add: () => $(document).on('keypress', callback)
    };
  };

  const _handleKeypress = e => {
    const letter = e.key.toLowerCase().trim();
    if (valid_letters.test(letter)) {
      guess(letter);
    }
  }

  function _addKeyHandler() {
    $(document).on('keypress', _handleKeypress);
  }

  function _removeKeyHandler() {
    $(document).off('keypress',_handleKeypress);
  }

  function guess(letter) {
    _state.last_guess = letter;
    api.guess(letter)
    .then(update)
    .catch(e => {
      console.log("Bad guess response", e); 
      return e.json()
      .then(({message}) => {
         _render_message(`<p>${message}</p>`);
         const msg = $('#'+ids.message);
         const lg = _state.letters_guessed;
         msg.find('p:first-child').addClass('error')
         msg.append(`<p>${lg.sort().join(' ')}</p>`);
      });
    });
  }

  // Initializes the application.
  // Recovers an existing game state
  // Or renders the title screen
  function init() {
    api.get_game()
    .then(start_game)
    .catch(response => {
      _render_title_scene();
    })
  }

  // Called once after title scene
  function start_game(state) {
    _addKeyHandler();
    hide_hangman();
    update(state);
  }
  
  // Updates the UI given game state
  function update(new_state) {
    _state = Object.assign(_state, new_state);
    console.log('Current state')
    console.log(JSON.stringify(new_state,null,'\t'));
    const { status } = new_state;
    if (status === 'ongoing') {
      _render_ongoing();
    } else if (status === 'won') {
      _removeKeyHandler();
      _render_won();
    } else if (status === 'lost') {
      _removeKeyHandler();
      _render_lost();
    } else {
      console.error("Unhandled game state: ", state);
      reset();
    }
  }

  // Requests a new game and starts it
  function new_game() {
    _state = {};
    api.new_game()
    .then(start_game)
    .catch(e => {
      console.log("Failed to new_game and make new game", e);
      reset();
    });
  }

  // Called on unrecoverable state. Refreshes the page.
  function reset() {
      window.location = window.location;
  }

  // render helpers
  
  function show_hangman() {
    containers.hangman.find('img.hidden').transition('fade in');
  }

  function hide_hangman() {
    containers.hangman.find('img').not('.hidden').transition('fade out');
  }

  function show_piece(i) {
    containers.hangman.find('img.hidden#'+ids.piece(i)).transition('fade in');
  }
  
  function _render_message(text) {
    let message = $('#'+ids.message);
    if (message.length) {
        message.html(text);
    } else {
        message = factory.message(text);
        containers.footer.append(message);
    }
    return message;
  }

  function _render_title() {
    let title = $('#'+ids.title);
    if (!title.length) {
        title = factory.title();
        containers.header.append(title);
    }
    return title;
  }

  function clear() {
    const { header, content, footer } = containers;
    header.empty();
    content.children().not('#'+ids.hangman).remove();
    footer.empty();
  }

  // Ongoing scene
  function _render_ongoing() {
    clear();
    const { 
      word_with_blanks,
      letters_guessed,
      guesses_left,
      incorrect_guesses,
      last_guess,
      max_guesses
    } = _state;
    const letter_text = `<p>${letters_guessed.sort().join(' ')}</p>`
    _render_title();
    _render_blanks(word_with_blanks);
    _render_counter(guesses_left);
    _render_message(`
      <p>
        ${last_guess ? `You guessed ${last_guess}` : ''}
      </p>
      ${letter_text}
    `);
    for (let i=0; i<incorrect_guesses; i++) {
      show_piece(i);
    }
  }

  function _render_blanks(word) {
    const { answer, status, letters_left } = _state;
    let ll = new Set(letters_left || []);
    let blanks = $('#'+ids.blanks);
    if (!blanks.length) {
      blanks = factory.blanks();
      containers.content.append(blanks);
    }
    for (let c of word) {
      let l = factory.letter(c);
      if (status === 'won') {
        l.find('h1').addClass('won');
      } else if (status === 'lost' && ll.has(c)) {
        l.find('h1').addClass('missed-letter');
      }
      blanks.append(l);
    }
    return blanks;
  }

  function _render_counter(n) {
    let counter = $('#'+ids.counter);
    if (!counter.length) {
      counter = factory.counter(n);
    } else {
      counter.html(n + ' guesses remaining');
    }
    return counter;
  }

  // Lost scene
  function _render_lost() {
    const { answer, won, lost } = _state;
    clear();
    show_hangman();
    _render_title();
    _render_blanks(answer);
    _render_message(`
      <p>You Lost!</p>
      <p>Wins: ${won} Losses: ${lost}</p>
    `);
    _render_play_again_btn();
  }

  // Won scene
  function _render_won() {
    const { answer, won, lost } = _state;
    clear();
    _render_title();
    _render_blanks(answer);
    _render_message(`
      <p>You won!</p>
      <p>Wins: ${won} Losses: ${lost}</p>
    `);
    _render_play_again_btn();
  }

  function _render_play_again_btn() {
    let btn = $('#'+ids.btn);
    if (btn.length)
        btn.remove();
    btn = factory.btn('Play again?');
    containers.footer.append(btn);
    const enterToPlay = enterToPress(btn);
    enterToPlay.add();
    btn.click(() => {
        enterToPlay.remove();
        new_game();
    });
    return btn;
  }

  // Initial title scene
  function _render_title_scene() {
    const { header, content, footer, hangman } = containers;
    const { directions, btn } = factory;
    clear();
    let startBtn = btn('Start Game!');
    let dirs = directions();
    let title = _render_title();
    content.append(dirs);
    footer.append(startBtn);

    // Animation
    let scene = $()
      .add(title)
      .add(dirs.children())
      .add(startBtn)
    scene.css('visibility','hidden');
    scene
      .transition({
        animation: 'fade down',
        duration: 400,
        interval: 300
      })
    show_hangman();

    // Apply start button callbacks
    const enterToStart = enterToPress(startBtn);
    enterToStart.add();
    startBtn.click(() => {
      api.new_game()
      .then(state => {
        enterToStart.remove();
        start_game(state);
      })
      .catch(e => {
        _removeKeyHandler();
        console.error(e);
      });
    });
  }

  init();
});
