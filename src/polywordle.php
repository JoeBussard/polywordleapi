<?php 

//require 'sage.phar';
//sage('hello world');

  function curl_game ($userId = "") {
    $ch = curl_init();
    $base_url = '127.0.0.1:5000/game';
    $game_url = $base_url . $userId;
    curl_setopt($ch, CURLOPT_URL, $game_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result_raw = curl_exec($ch);
    $result_json = json_decode($result_raw, true);
    return $result_json;
    curl_close($ch);
  }

  if (isset($_POST['user_id'])){
    $result = curl_game($_POST['user_id']);
    $user_id = $_POST['user_id'];
  }
  else{
    $result = curl_game();
    $user_id = $result['user_id'];
  }

/*
  $ch = curl_init();
  $base_url = '127.0.0.1:5000/game/curl_1';
  $username = 'curl_1';
  $action = 'newgame';
  #$combined_url = $base_url + $username + $action;
  $combined_url = $base_url;
  curl_setopt($ch, CURLOPT_URL, $combined_url);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  $result = curl_exec($ch);
  curl_close($ch);*/
?>
<html>
<head>
<title>Testing polywordle in php</title>
</head>
<h1>Results</h1>
<p><?php
 // echo $result;
  //echo gettype($result);
  //echo("dumping");
 //i echo ' \n\n\n\n\n';
//  echo '<pre>' . var_export($result, true) . '</pre>' ;

//  $obj = json_decode($result, true);
  $obj = $result;
//  sage($obj);
//  sage($obj_false);
  //echo("----@@@@@@@@@@@@------------------");
  echo("Polywordle for: ");
  if (null != $obj) {
  echo $obj['user_id'];
  $keyboard_map = $obj['keyboard_map'];
  $keys = array_keys($keyboard_map);
//  sage($keys);
  $better_map = array();
  $progress_stack = $obj['progress_grid_history'];
 // sage($progress_stack);
  $guess_array = $obj['guesses'];
  sage($guess_array);
  }
  $style_array = array(
    "present"=>"orange",
    "absent"=>"red",
    "plain"=>"gray",
    "correct"=>"green"
  );

  foreach($guess_array as $guess){
    foreach ($guess as $letterColorPair){ //guessLetter=>$guessColor){
      /*sage($letterColorPair);
      sage($letterColorPair[0]);
      sage($letterColorPair[1]);
      sage($style_array['present']);
      sage($style_array[$letterColorPair[1]]);*/
      $thisColor = $style_array[$letterColorPair[1]];
      $thisLetter = $letterColorPair[0];
      echo nl2br("<span style='color:$thisColor'>$thisLetter</span>");
    }
    echo nl2br("\n");
  }

  foreach($progress_stack as $bar){
    $progress_string = implode(" ", $bar);
    echo nl2br("\n" . $progress_string);
  }

  function curl_new_guess ($guess, $user_id){
    $ch = curl_init();
    $base_url = '127.0.0.1:5000/game/' . $user_id;
    $guess_url = $base_url . '/' . $guess;
    curl_setopt($ch, CURLOPT_URL, $guess_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result_raw = curl_exec($ch);
    $result_json = json_decode($result_raw, true);
    return $result_json;
  }
  if (isset($_POST['submitNewGuess']) && isset($_POST['newGuess'])){
    $result = curl_new_guess($_POST['newGuess'], $user_id);
  }
  function curl_new_game () {
    $ch = curl_init();
    $base_url = '127.0.0.1:5000/game';
    curl_setopt($ch, CURLOPT_URL, $base_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result_raw = curl_exec($ch);
    $result_json = json_decode($result_raw, true);
    return $result_json;
  }


?>

</br>
<h3>Make your next guess.</h3>
<form action = "" method='post'>
<p><strong>My Next 5 Letter Word is...</strong></p>
<input type='text' name='newGuess' maxlength='5'/>
<input type='submit' name='submitNewGuess'/>
</form>
<h3>Start A New Game?</h3>
<form action = '' method='post'>
<p><strong>I want to start a new game...</strong></p>
<input type='submit' name='submitStartNewGame'/>
</form>
<?php


  echo "<span style='color:gray" . "'>";
  echo nl2br("\n White letters\n");
    foreach($keyboard_map as $letter=>$status){
      if($status == 'plain'){
      echo nl2br(" " . $letter);
    }
  }
  echo "</span>";

  echo "<span style='color:Green" . "'>";
  echo nl2br("\n Green letters\n");
  foreach($keyboard_map as $letter=>$status){
    if ($status == 'correct'){
      echo nl2br(" " . $letter)  ;
    }
  }
  echo "</span>";

  echo "<span style='color:Orange" . "'>";
  echo nl2br("\n Yellow letters\n");
  foreach($keyboard_map as $letter=>$status){
    if ($status == 'present'){
      echo nl2br(" " . $letter)  ;
    }
  }
  echo "</span>";

  echo "<span style='color:Red" . "'>";
  echo nl2br("\n Red letters\n");
  foreach($keyboard_map as $letter=>$status){
    if ($status == 'absent'){
      echo nl2br(" " . $letter)  ;
    }
  }
  echo "</span>";


?>
</p>
</html>
