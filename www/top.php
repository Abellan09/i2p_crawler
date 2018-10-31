<html>
	<body>
		<?php
			$myPDO = new PDO('sqlite:i2p_database.db');
			if ($myPDO->connect_error) {
				die("Connection failed: " . $myPDO->connect_error);
			} 
			$id = $_POST["bola"];
			$type = $_POST["type"];
			if ($type == "incoming") {
				$top_id = $myPDO->query("SELECT node_id FROM Incoming_Top WHERE id=$id");
			}
			elseif ($type == "outgoing") {
				$top_id = $myPDO->query("SELECT node_id FROM Outgoing_Top WHERE id=$id");
			}
			else {
				echo "Type must be 'outgoing' or 'incoming'";
			}
			if ($top_id->num_rows >= 0) {
				foreach($top_id as $row)
				{
					$top_id = $row['node_id'];
				}
				$result = $myPDO->query("SELECT id, name, outgoing_sites, incoming_sites, degree FROM Nodes WHERE id=$top_id");
				if ($result->num_rows >= 0) {
					foreach($result as $row)
					{
						echo "<u><b>TOP " . $id . "<br/>" . "<br/></b></u>";
						echo "Name:" . "&nbsp;&nbsp;" . $row['name'] . "<br/>";
						echo "ID:" . "&nbsp;&nbsp;" . $row['id'] . "<br/>";
						echo "Outgoing Sites:" . "&nbsp;&nbsp;" . $row['outgoing_sites'] . "<br/>";
						echo "Incoming Sites:" . "&nbsp;&nbsp;" . $row['incoming_sites'] . "<br/>";
						echo "Degree:" . "&nbsp;&nbsp;" . $row['degree'];
					}
				}
				else {
					echo "The query does not return anything";
				}
			}
			else {
				echo "The query does not return anything";
			}
		?>
	</body>
</html>