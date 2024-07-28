<?php
include '../config.php';

$names = $_POST['nama'];
$types = $_POST['tipe'];

for ($i = 0; $i < count($names); $i++) {
    $nama = $names[$i];
    $tipe = $types[$i];

    mysqli_query($config, "INSERT INTO kriteria (nm_kriteria, tipe) VALUES ('$nama', '$tipe')");
}

header("location: ../tampil/datakriteria.php");
?>