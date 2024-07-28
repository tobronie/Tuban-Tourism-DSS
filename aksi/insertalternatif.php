<?php
include '../config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['nama']) && is_array($_POST['nama'])) {
        $nama_values = array_map(function ($value) use ($config) {
            return mysqli_real_escape_string($config, $value);
        }, $_POST['nama']);
        foreach ($nama_values as $nama) {
            mysqli_query($config, "INSERT INTO alternatif (nm_alternatif) VALUES ('$nama')");
        }
        header("location: ../tampil/dataalternatif.php");
        exit();
    } else {
        echo "Error: Invalid form data.";
    }
} else {
    echo "Form not submitted!";
}
?>