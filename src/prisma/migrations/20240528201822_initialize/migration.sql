-- CreateTable
CREATE TABLE "Node" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "ip" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "weight" REAL NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Node_ip_key" ON "Node"("ip");
