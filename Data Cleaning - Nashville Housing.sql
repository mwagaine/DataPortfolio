/*
Cleaning Data in SQL Queries
*/


Select *
From PortfolioProject.dbo.NashvilleHousing


-- 1. POPULATE MISSING PropertyAddress DATA

-- Check to see if there is any missing PropertyAddress data.

Select *
From PortfolioProject.dbo.NashvilleHousing
Where PropertyAddress is null
Order by ParcelID

-- In the USA, Parcel ID is a unique identifier for a unit of land. 
-- Since housing properties are built on specific units of land, 
-- we can associate each PropertyAddress with a specific ParcelID.

Select a.ParcelID, a.PropertyAddress, b.ParcelID, b.PropertyAddress, ISNULL(a.PropertyAddress, b.PropertyAddress) 
From PortfolioProject.dbo.NashvilleHousing a
Join PortfolioProject.dbo.NashvilleHousing b
	on a.ParcelID = b.ParcelID
	AND a.UniqueID <> b.UniqueID
Where a.PropertyAddress is null

-- The PropertyAddress values in the last column should now replace 
-- the null values in the second column, since they are both associated
-- with the same ParcelID and therefore the same unit of land.

Update a
SET PropertyAddress = ISNULL(a.PropertyAddress, b.PropertyAddress)
From PortfolioProject.dbo.NashvilleHousing a
Join PortfolioProject.dbo.NashvilleHousing b
	on a.ParcelID = b.ParcelID
	AND a.UniqueID <> b.UniqueID
Where a.PropertyAddress is null

-- Check to see if all missing PropertyAddress values have been replaced

Select PropertyAddress
From PortfolioProject.dbo.NashvilleHousing
Where PropertyAddress is null


----------------------------------------------------------------------------------


-- 2. SPLIT PropertyAddress INTO INDIVIDUAL COLUMNS (ADDRESS, CITY)

Select PropertyAddress
From PortfolioProject.dbo.NashvilleHousing

Select SUBSTRING(PropertyAddress, 1, CHARINDEX(',', PropertyAddress) - 1) as Address,
	   SUBSTRING(PropertyAddress, CHARINDEX(',', PropertyAddress) + 2, LEN(PropertyAddress)) as City 
From PortfolioProject.dbo.NashvilleHousing

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Add PropertySplitAddress Nvarchar(255);

Update PortfolioProject.dbo.NashvilleHousing
SET PropertySplitAddress = SUBSTRING(PropertyAddress, 1, CHARINDEX(',', PropertyAddress) - 1)

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Add PropertySplitCity Nvarchar(255);

Update PortfolioProject.dbo.NashvilleHousing
SET PropertySplitCity = SUBSTRING(PropertyAddress, CHARINDEX(',', PropertyAddress) + 2, LEN(PropertyAddress))

Select *
From PortfolioProject.dbo.NashvilleHousing


----------------------------------------------------------------------------------


-- 3. SPLIT OwnerAddress INTO INDIVIDUAL COLUMNS (ADDRESS, CITY, STATE)

-- Use PARSENAME function to split this column:
-- Note that this function works from right-to-left of string (not the reverse) 
-- and only recognises full stops as delimiters within strings, not commas.

Select OwnerAddress
From PortfolioProject.dbo.NashvilleHousing

Select PARSENAME(REPLACE(OwnerAddress, ',', '.'), 3) as Address,
       PARSENAME(REPLACE(OwnerAddress, ',', '.'), 2) as City,
	   PARSENAME(REPLACE(OwnerAddress, ',', '.'), 1) as State
From PortfolioProject.dbo.NashvilleHousing

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Add OwnerSplitAddress Nvarchar(255);

Update PortfolioProject.dbo.NashvilleHousing
SET OwnerSplitAddress = PARSENAME(REPLACE(OwnerAddress, ',', '.'), 3)

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Add OwnerSplitCity Nvarchar(255);

Update PortfolioProject.dbo.NashvilleHousing
SET OwnerSplitCity = PARSENAME(REPLACE(OwnerAddress, ',', '.'), 2)

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Add OwnerSplitState Nvarchar(255);

Update PortfolioProject.dbo.NashvilleHousing
SET OwnerSplitState = PARSENAME(REPLACE(OwnerAddress, ',', '.'), 1)

Select *
From PortfolioProject.dbo.NashvilleHousing

-- Although there is missing data for the new OwnerAddress columns and a lot
-- of the available OwnerAddress data matches that of PropertyAddress, note
-- that in the USA the owner address is the equivalent of the mailing address
-- which doesn't necessarily have be the same as the property address.
-- So we don't need to populate this missing data as we did for PropertyAddress.


----------------------------------------------------------------------------------


-- 4. CHANGE Y AND N VALUES TO YES AND NO RESPECTIVELY IN SoldAsVacant FIELD

Select Distinct(SoldAsVacant), Count(SoldAsVacant)
From PortfolioProject.dbo.NashvilleHousing
Group by SoldAsVacant
Order by 1

Select SoldAsVacant,
       CASE When SoldAsVacant = 'N' THEN 'No'
	        When SoldAsVacant = 'Y' THEN 'Yes'
	   ELSE SoldAsVacant
	   END
From PortfolioProject.dbo.NashvilleHousing
Where SoldAsVacant IN ('N', 'Y')

Update PortfolioProject.dbo.NashvilleHousing
SET SoldAsVacant = CASE When SoldAsVacant = 'N' THEN 'No'
	                    When SoldAsVacant = 'Y' THEN 'Yes'
	               ELSE SoldAsVacant
	               END

Select Distinct(SoldAsVacant), Count(SoldAsVacant)
From PortfolioProject.dbo.NashvilleHousing
Group by SoldAsVacant
Order by 1


----------------------------------------------------------------------------------


-- 6. DELETE DUPLICATE ROWS

-- Use CTE to label original rows as '1' and their duplicates as '2' or more.

With RowedTable AS 
(
Select *,
       ROW_NUMBER() OVER (PARTITION BY ParcelID,
	                                   PropertyAddress,
					                   SalePrice,
					                   SaleDate,
					                   LegalReference
					                   ORDER BY UniqueID) row_num
From PortfolioProject.dbo.NashvilleHousing
)
Select Distinct *
From RowedTable

-- Check for any duplicate rows without scrolling through all the data: 
-- all rows should be labeled '1' in the row_num field if there are no duplicates.

With RowedTable AS 
(
Select *,
       ROW_NUMBER() OVER (PARTITION BY ParcelID,
	                                   PropertyAddress,
					                   SalePrice,
					                   SaleDate,
					                   LegalReference
					                   ORDER BY UniqueID) row_num
From PortfolioProject.dbo.NashvilleHousing
)
Select Distinct row_num
From RowedTable

-- Display all the duplicate rows.

With RowedTable AS 
(
Select *,
       ROW_NUMBER() OVER (PARTITION BY ParcelID,
	                                   PropertyAddress,
					                   SalePrice,
					                   SaleDate,
					                   LegalReference
					                   ORDER BY UniqueID) row_num
From PortfolioProject.dbo.NashvilleHousing
)
Select *
From RowedTable
Where row_num > 1

-- Now delete these duplicate rows.

With RowedTable AS 
(
Select *,
       ROW_NUMBER() OVER (PARTITION BY ParcelID,
	                                   PropertyAddress,
					                   SalePrice,
					                   SaleDate,
					                   LegalReference
					                   ORDER BY UniqueID) row_num
From PortfolioProject.dbo.NashvilleHousing
)
DELETE
From RowedTable
Where row_num > 1

-- Check to see if duplicates have been deleted and if there are anymore left.

With RowedTable AS 
(
Select *,
       ROW_NUMBER() OVER (PARTITION BY ParcelID,
	                                   PropertyAddress,
					                   SalePrice,
					                   SaleDate,
					                   LegalReference
					                   ORDER BY UniqueID) row_num
From PortfolioProject.dbo.NashvilleHousing
)
Select *
From RowedTable
Where row_num > 1


----------------------------------------------------------------------------------


-- 7. DELETE UNNECCESARY COLUMNS

-- After splitting the PropertyAddress and OwnerAddress columns, 
-- they are now redundant so can be deleted.

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
DROP COLUMN PropertyAddress, OwnerAddress

Select *
From PortfolioProject.dbo.NashvilleHousing



Select *,
       ROW_NUMBER() OVER (PARTITION BY ParcelID,
	                                   PropertyAddress,
					                   SalePrice,
					                   SaleDate,
					                   LegalReference
					                   ORDER BY UniqueID) row_num
From PortfolioProject.dbo.NashvilleHousing
Order by ParcelID

Select *
From PortfolioProject.dbo.NashvilleHousing


----------------------------------------------------------------------------------


-- 8. CHANGE DATE FORMAT

-- Compare current format with desired format. 

Select SaleDate,
       CONVERT(date, SaleDate)
From PortfolioProject.dbo.NashvilleHousing

-- Attempt to edit SaleDate column accordingly. 

Update PortfolioProject.dbo.NashvilleHousing
SET SaleDate = CONVERT(date, SaleDate)

Select SaleDate,
From PortfolioProject.dbo.NashvilleHousing

-- If the above method doesn't work, try this instead:

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Add SalesDateConverted Date;

Update PortfolioProject.dbo.NashvilleHousing
SET SalesDateConverted = CONVERT(date, SaleDate)

Select SaleDate,
       SalesDateConverted
From PortfolioProject.dbo.NashvilleHousing
Where SalesDateConverted <> CONVERT(date, SaleDate)

-- Now delete redundant SaleDate column

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
DROP COLUMN SaleDate

Select *
From PortfolioProject.dbo.NashvilleHousing
