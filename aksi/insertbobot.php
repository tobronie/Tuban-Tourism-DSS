<?php
include '../config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!empty($_POST['nm_kriteria']) && !empty($_POST['value'])) {
        $id_kriterias = $_POST['nm_kriteria'];
        $values = $_POST['value'];
        $count = count($id_kriterias);
        for ($i = 0; $i < $count; $i++) {
            $id_kriteria = mysqli_real_escape_string($config, $id_kriterias[$i]);
            $value = mysqli_real_escape_string($config, $values[$i]);
            $query = "INSERT INTO bobot (id_kriteria, value) VALUES ('$id_kriteria', '$value')";

            if (!mysqli_query($config, $query)) {
                echo "Error: " . mysqli_error($config);
                exit();
            }
        }
        header("location: ../tampil/databobot.php");
        exit();
    } else {
        echo "Error: Form data is incomplete.";
    }
} else {
    echo "Form not submitted!";
}
?>