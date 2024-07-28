<?php
    include '../config.php';

    $id_skala = $_GET['id_skala'];

    mysqli_query($config,  "delete from skala WHERE id_skala='$id_skala'");

    header("location: ../tampil/dataskala.php");
?>